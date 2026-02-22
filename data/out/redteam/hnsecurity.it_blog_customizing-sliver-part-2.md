# https://hnsecurity.it/blog/customizing-sliver-part-2/

[Skip to main content](https://hnsecurity.it/blog/customizing-sliver-part-2/#sections-container)

![Silver Framework logo](https://hnsecurity.it/wp-content/uploads/2025/09/SILVER-uai-836x836.jpg)

# Customizing Sliver – Part 2

October 24, 2023\|[![Alessandro Iandoli](https://secure.gravatar.com/avatar/644822f5d8329ca419a50c1f39c97de5ccd163d1932e4cdc60a6cc8cb64ed29e?s=40&d=mm&r=g)](https://hnsecurity.it/blog/author/ale98/) By [Alessandro Iandoli](https://hnsecurity.it/blog/author/ale98/)

[Articles](https://hnsecurity.it/blog/category/articles/ "View all posts in Articles"), [Tools](https://hnsecurity.it/blog/category/tools/ "View all posts in Tools")

Hello! This is the second part of the three-part blog [series](https://hnsecurity.it/tag/sliver/) explaining how to customize [Sliver C2](https://github.com/BishopFox/sliver) by adding your own commands.

In this part I’m going to provide an **overview of the communication model** in Sliver C2, by examining the flow of function calls performed by the components when an operator launches a command.

In [part 3](https://hnsecurity.it/blog/customizing-sliver-part-3/), I’ll provide a tutorial showing how to create the first simple command from scratch in Sliver C2.

## Communication model overview

As explained [here](https://github.com/BishopFox/sliver/wiki/Architecture), Sliver works in the following way:

![](https://cdn-images-1.medium.com/max/1000/1*yv3zWNq_EK4QPUU9fqAEng.png)Communication model diagram1\. When the operator types a command in the console, the client serializes the command in a protobuf request and sends it, through gRPC, to the server.

2\. The server processes the message and forwards the protobuf request to the implant, through the **communication channel** **in use with the implant** (could be HTTP/S, DNS, Wireguard; in the diagram above it’s HTTP).

3\. The implant **unserializes** the protobuf request, executes the specified task, **serializes the output** again in a **protobuf message**, and sends it to the server through the **same communication channel used at step 2**.

4\. The server receives the protobuf response and forwards it to the client through **gRPC**. At this point the client simply unserializes the **protobuf response** and prints the output to the screen.

### Client-server communication

The **services.proto** file, by importing **client.proto** and **sliver.proto,** defines The **gRPC messages** **and methods** exchanged between client and server.

The client stores all the commands in [client/command/sliver.go](https://github.com/BishopFox/sliver/blob/master/client/command/sliver.go). All commands stored in the file will call functions defined under **client/command/<command folder>/<command\_name>.go**. For example, sliver.go defines the command **execute-assembly**, that when typed in by the operator, invokes function **ExecuteAssemblyCmd()**, defined in [client/command/exec/execute-assembly.go](https://github.com/BishopFox/sliver/blob/master/client/command/exec/execute-assembly.go).

All these functions will end up calling **gRPC functions** defined in [services.proto](https://github.com/BishopFox/sliver/blob/master/protobuf/rpcpb/services.proto). For example, **ExecuteAssemblyCmd()** calls **con.Rpc.ExecuteAssembly()** defined in services.proto.

![](https://cdn-images-1.medium.com/max/1000/1*2DWIHeNftjljtKCLNncPYQ.png)Mapping between con.Rpc.ExecuteAssembly() and definition in services.proto

Actually, [services\_grpc.pb.go](https://github.com/BishopFox/sliver/blob/master/protobuf/rpcpb/services_grpc.pb.go) defines **con.Rpc.ExecuteAssembly()**. **Protoc** automatically builds the file services\_grpc.pb.go starting from the definitions inside services.proto.

_As I’ll outline later, we will only have to_ **_modify services.proto, sliver.proto, and client.proto and then rebuild services\_grpc.pb.go_** _by just running **m**_ **_ake pb_** _, in order to add our custom commands._

These gRPC functions send protobuf messages to the server through gRPC, where [server/rpc/rpc-\*.go](https://github.com/BishopFox/sliver/tree/master/server/rpc) defines the corresponding server-side handlers for these gRPC functions. For example, [server/rpc/rpc-tasks.go](https://github.com/BishopFox/sliver/blob/master/server/rpc/rpc-tasks.go) defines [ExecuteAssembly()](https://github.com/BishopFox/sliver/blob/master/server/rpc/rpc-tasks.go#L127), the server-side function that handles the **con.Rpc.ExecuteAssembly()** request performed by the client.

These server functions handling the gRPC requests will perform the required processing and then send the response with the statement:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

return resp, nil

return resp, nil

```
return resp, nil
```

For the **ExecuteAssembly()** handler function, this sends a protobuf message to the implant and then returns the response, as we will see in the following section.

### Server-implant communication

The **sliver.proto** file defines the messages that are exchanged between server and implant. Server and implant exchange these messages not through gRPC but through HTTP/S, DNS depending on how the implant was generated, as previously mentioned.

Let’s inspect the function [ExecuteAssembly()](https://github.com/BishopFox/sliver/blob/master/server/rpc/rpc-tasks.go#L127) in order to explain what the server is going to do in this case:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

// ExecuteAssembly - Execute a .NET assembly on the remote system in-memory (Windows only)

func(rpc \*Server)ExecuteAssembly(ctx context.Context, req \*sliverpb.ExecuteAssemblyReq)(\*sliverpb.ExecuteAssembly, error){

var session \*core.Session

var beacon \*models.Beacon

var err error

if !req.Request.Async{

session = core.Sessions.Get(req.Request.SessionID)

if session == nil{

returnnil, ErrInvalidSessionID

}

}else{

beacon, err = db.BeaconByID(req.Request.BeaconID)

if err != nil{

tasksLog.Errorf("%s", err)

returnnil, ErrDatabaseFailure

}

if beacon == nil{

returnnil, ErrInvalidBeaconID

}

}

shellcode, err := generate.DonutFromAssembly(

req.Assembly,

req.IsDLL,

req.Arch,

req.Arguments,

req.Method,

req.ClassName,

req.AppDomain,

)

if err != nil{

tasksLog.Errorf("Execute assembly failed: %s", err)

returnnil, err

}

resp := &sliverpb.ExecuteAssembly{Response: &commonpb.Response{}}

if req.InProcess{

tasksLog.Infof("Executing assembly in-process")

invokeInProcExecAssembly := &sliverpb.InvokeInProcExecuteAssemblyReq{

Data: req.Assembly,

Runtime: req.Runtime,

Arguments: strings.Split(req.Arguments, " "),

AmsiBypass: req.AmsiBypass,

EtwBypass: req.EtwBypass,

Request: req.Request,

}

err = rpc.GenericHandler(invokeInProcExecAssembly, resp)

}else{

invokeExecAssembly := &sliverpb.InvokeExecuteAssemblyReq{

Data: shellcode,

Process: req.Process,

Request: req.Request,

PPid: req.PPid,

ProcessArgs: req.ProcessArgs,

}

err = rpc.GenericHandler(invokeExecAssembly, resp)

}

if err != nil{

returnnil, err

}

return resp, nil

}<span class="pre--content"></span>

// ExecuteAssembly - Execute a .NET assembly on the remote system in-memory (Windows only)
func (rpc \*Server) ExecuteAssembly(ctx context.Context, req \*sliverpb.ExecuteAssemblyReq) (\*sliverpb.ExecuteAssembly, error) {
var session \*core.Session
var beacon \*models.Beacon
var err error
if !req.Request.Async {
session = core.Sessions.Get(req.Request.SessionID)
if session == nil {
return nil, ErrInvalidSessionID
}
} else {
beacon, err = db.BeaconByID(req.Request.BeaconID)
if err != nil {
tasksLog.Errorf("%s", err)
return nil, ErrDatabaseFailure
}
if beacon == nil {
return nil, ErrInvalidBeaconID
}
}

shellcode, err := generate.DonutFromAssembly(
req.Assembly,
req.IsDLL,
req.Arch,
req.Arguments,
req.Method,
req.ClassName,
req.AppDomain,
)
if err != nil {
tasksLog.Errorf("Execute assembly failed: %s", err)
return nil, err
}

resp := &sliverpb.ExecuteAssembly{Response: &commonpb.Response{}}
if req.InProcess {
tasksLog.Infof("Executing assembly in-process")
invokeInProcExecAssembly := &sliverpb.InvokeInProcExecuteAssemblyReq{
Data: req.Assembly,
Runtime: req.Runtime,
Arguments: strings.Split(req.Arguments, " "),
AmsiBypass: req.AmsiBypass,
EtwBypass: req.EtwBypass,
Request: req.Request,
}
err = rpc.GenericHandler(invokeInProcExecAssembly, resp)
} else {
invokeExecAssembly := &sliverpb.InvokeExecuteAssemblyReq{
Data: shellcode,
Process: req.Process,
Request: req.Request,
PPid: req.PPid,
ProcessArgs: req.ProcessArgs,
}
err = rpc.GenericHandler(invokeExecAssembly, resp)

}
if err != nil {
return nil, err
}
return resp, nil
}<span class="pre--content"> </span>

```
// ExecuteAssembly - Execute a .NET assembly on the remote system in-memory (Windows only)
func (rpc *Server) ExecuteAssembly(ctx context.Context, req *sliverpb.ExecuteAssemblyReq) (*sliverpb.ExecuteAssembly, error) {
 var session *core.Session
 var beacon *models.Beacon
 var err error
 if !req.Request.Async {
  session = core.Sessions.Get(req.Request.SessionID)
  if session == nil {
   return nil, ErrInvalidSessionID
  }
 } else {
  beacon, err = db.BeaconByID(req.Request.BeaconID)
  if err != nil {
   tasksLog.Errorf("%s", err)
   return nil, ErrDatabaseFailure
  }
  if beacon == nil {
   return nil, ErrInvalidBeaconID
  }
 }

 shellcode, err := generate.DonutFromAssembly(
  req.Assembly,
  req.IsDLL,
  req.Arch,
  req.Arguments,
  req.Method,
  req.ClassName,
  req.AppDomain,
 )
 if err != nil {
  tasksLog.Errorf("Execute assembly failed: %s", err)
  return nil, err
 }

 resp := &sliverpb.ExecuteAssembly{Response: &commonpb.Response{}}
 if req.InProcess {
  tasksLog.Infof("Executing assembly in-process")
  invokeInProcExecAssembly := &sliverpb.InvokeInProcExecuteAssemblyReq{
   Data:       req.Assembly,
   Runtime:    req.Runtime,
   Arguments:  strings.Split(req.Arguments, " "),
   AmsiBypass: req.AmsiBypass,
   EtwBypass:  req.EtwBypass,
   Request:    req.Request,
  }
  err = rpc.GenericHandler(invokeInProcExecAssembly, resp)
 } else {
  invokeExecAssembly := &sliverpb.InvokeExecuteAssemblyReq{
   Data:        shellcode,
   Process:     req.Process,
   Request:     req.Request,
   PPid:        req.PPid,
   ProcessArgs: req.ProcessArgs,
  }
  err = rpc.GenericHandler(invokeExecAssembly, resp)

 }
 if err != nil {
  return nil, err
 }
 return resp, nil
}
```

The req parameter passed as input corresponds to the protobuf message **ExecuteAssemblyReq,** defined in [sliver.proto](https://github.com/BishopFox/sliver/blob/master/protobuf/sliverpb/sliver.proto), in the following way (commonpb.Request is defined in [common.proto](https://github.com/BishopFox/sliver/blob/master/protobuf/commonpb/common.proto) but I added it here for clarity):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

common.proto

...

...

// Request - Common fields used in all gRPC requests

message Request {

bool Async = 1;

int64 Timeout = 2;

string BeaconID = 8;

string SessionID = 9;

}

...

...

\-\-\-------------------------------------------------------------------

sliver.proto

...

...

message ExecuteAssemblyReq {

bytes Assembly = 1;

string Arguments = 2;

string Process = 3;

bool IsDLL = 4;

string Arch = 5;

string ClassName = 6;

string Method = 7;

string AppDomain = 8;

uint32 PPid = 10;

repeated string ProcessArgs = 11;

// In process specific fields

bool InProcess = 12;

string Runtime = 13;

bool AmsiBypass = 14;

bool EtwBypass = 15;

commonpb.Request Request = 9;

}

...

...

common.proto
...
...
// Request - Common fields used in all gRPC requests
message Request {
bool Async = 1;
int64 Timeout = 2;

string BeaconID = 8;
string SessionID = 9;
}
...
...

\-\-\-------------------------------------------------------------------
sliver.proto
...
...
message ExecuteAssemblyReq {
bytes Assembly = 1;
string Arguments = 2;
string Process = 3;
bool IsDLL = 4;
string Arch = 5;
string ClassName = 6;
string Method = 7;
string AppDomain = 8;
uint32 PPid = 10;
repeated string ProcessArgs = 11;
// In process specific fields
bool InProcess = 12;
string Runtime = 13;
bool AmsiBypass = 14;
bool EtwBypass = 15;
commonpb.Request Request = 9;
}
...
...

```
common.proto
...
...
// Request - Common fields used in all gRPC requests
message Request {
  bool Async = 1;
  int64 Timeout = 2;

  string BeaconID = 8;
  string SessionID = 9;
}
...
...

---------------------------------------------------------------------
sliver.proto
...
...
message ExecuteAssemblyReq {
  bytes Assembly = 1;
  string Arguments = 2;
  string Process = 3;
  bool IsDLL = 4;
  string Arch = 5;
  string ClassName = 6;
  string Method = 7;
  string AppDomain = 8;
  uint32 PPid = 10;
  repeated string ProcessArgs = 11;
  // In process specific fields
  bool InProcess = 12;
  string Runtime = 13;
  bool AmsiBypass = 14;
  bool EtwBypass = 15;
  commonpb.Request Request = 9;
}
...
...
```

So what happens is that the handler performs the following actions:

1. retrieve the implant ID through req.Request.SessionID/req.Request.BeaconID and check if it is valid.
2. create the go struct **sliverpb.ExecuteAssembly** that corresponds to the **ExecuteAssembly** protobuf message defined in **sliver.proto. This struct will contain the response from the implant**.
3. create the go struct **sliverpb.InvokeInProcExecuteAssemblyReq** that corresponds to the **InvokeInProcExecuteAssemblyReq** protobuf message defined in **sliver.proto**(we suppose the we executed execute-assembly in process, with the -i flag, otherwise the server will create ExecuteAssemblyReq). **The implant will receive this struct as a request to process**.
4. call **rpc.GenericHandler(),** **passing as input the request and the response created at steps 2 and 3**.
5. return **resp**, the response struct that the rpc.GenericHandler function populates with the response of the implant.

Here’s the body of function **rpc.GenericHandler()**, defined inside [server/rpc/rpc.go](https://github.com/BishopFox/sliver/blob/master/server/rpc/rpc.go):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

// GenericHandler - Pass the request to the Sliver/Session

func(rpc \*Server)GenericHandler(req GenericRequest, resp GenericResponse) error {

var err error

request := req.GetRequest()

if request == nil{

return ErrMissingRequestField

}

if request.Async{

err = rpc.asyncGenericHandler(req, resp)

return err

}

// Sync request

session := core.Sessions.Get(request.SessionID)

if session == nil{

return ErrInvalidSessionID

}

// Overwrite unused implant fields before re-serializing

request.SessionID = ""

request.BeaconID = ""

reqData, err := proto.Marshal(req)

if err != nil{

return err

}

data, err := session.Request(sliverpb.MsgNumber(req), rpc.getTimeout(req), reqData)

if err != nil{

return err

}

err = proto.Unmarshal(data, resp)

if err != nil{

return err

}

return rpc.getError(resp)

}

// GenericHandler - Pass the request to the Sliver/Session
func (rpc \*Server) GenericHandler(req GenericRequest, resp GenericResponse) error {
var err error
request := req.GetRequest()
if request == nil {
return ErrMissingRequestField
}
if request.Async {
err = rpc.asyncGenericHandler(req, resp)
return err
}

// Sync request
session := core.Sessions.Get(request.SessionID)
if session == nil {
return ErrInvalidSessionID
}

// Overwrite unused implant fields before re-serializing
request.SessionID = ""
request.BeaconID = ""

reqData, err := proto.Marshal(req)
if err != nil {
return err
}

data, err := session.Request(sliverpb.MsgNumber(req), rpc.getTimeout(req), reqData)
if err != nil {
return err
}
err = proto.Unmarshal(data, resp)
if err != nil {
return err
}
return rpc.getError(resp)
}

```
// GenericHandler - Pass the request to the Sliver/Session
func (rpc *Server) GenericHandler(req GenericRequest, resp GenericResponse) error {
    var err error
    request := req.GetRequest()
    if request == nil {
        return ErrMissingRequestField
    }
    if request.Async {
        err = rpc.asyncGenericHandler(req, resp)
        return err
    }

    // Sync request
    session := core.Sessions.Get(request.SessionID)
    if session == nil {
        return ErrInvalidSessionID
    }

    // Overwrite unused implant fields before re-serializing
    request.SessionID = ""
    request.BeaconID = ""

    reqData, err := proto.Marshal(req)
    if err != nil {
        return err
    }

    data, err := session.Request(sliverpb.MsgNumber(req), rpc.getTimeout(req), reqData)
    if err != nil {
        return err
    }
    err = proto.Unmarshal(data, resp)
    if err != nil {
        return err
    }
    return rpc.getError(resp)
}
```

You may notice that the function retrieves the beacon/session implant, **serializes the request, sends the serialized request to the implant**, and finally **returns the response from the implant inside the resp input parameter**.

On the implant-side, the functions in charge of handling the requests coming from the server are defined inside **handlers\_<OS>.go** and **handlers.go.** The file **handlers.go contains handlers for tasks that can be executed on any OS**, while **handlers\_<OS>.go contains handlers for tasks that can be executed only on a specific OS**. For example, [handlers\_windows.go](https://github.com/BishopFox/sliver/blob/master/implant/sliver/handlers/handlers_windows.go) contains **impersonateHandler()** that implements the impersonate command that would be **useful only with a Windows OS**, while **handlers.go contains dirListHandler()** that implements the ls command that is **useful with any OS**.

Let’s inspect the **inProcExecuteAssemblyHandler()** defined in [implant/sliver/handlers\_windows.go](https://github.com/BishopFox/sliver/blob/master/implant/sliver/handlers/handlers_windows.go):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

funcinProcExecuteAssemblyHandler(data \[\]byte, resp RPCResponse){

execReq := &sliverpb.InvokeInProcExecuteAssemblyReq{}

err := proto.Unmarshal(data, execReq)

if err != nil{

// {{if .Config.Debug}}

log.Printf("error decoding message: %v", err)

// {{end}}

return

}

output, err := taskrunner.InProcExecuteAssembly(execReq.Data, execReq.Arguments, execReq.Runtime, execReq.AmsiBypass, execReq.EtwBypass)

execAsm := &sliverpb.ExecuteAssembly{Output: \[\]byte(output)}

if err != nil{

execAsm.Response = &commonpb.Response{

Err: err.Error(),

}

}

data, err = proto.Marshal(execAsm)

resp(data, err)

}

func inProcExecuteAssemblyHandler(data \[\]byte, resp RPCResponse) {
execReq := &sliverpb.InvokeInProcExecuteAssemblyReq{}
err := proto.Unmarshal(data, execReq)
if err != nil {
// {{if .Config.Debug}}
log.Printf("error decoding message: %v", err)
// {{end}}
return
}
output, err := taskrunner.InProcExecuteAssembly(execReq.Data, execReq.Arguments, execReq.Runtime, execReq.AmsiBypass, execReq.EtwBypass)
execAsm := &sliverpb.ExecuteAssembly{Output: \[\]byte(output)}
if err != nil {
execAsm.Response = &commonpb.Response{
Err: err.Error(),
}
}
data, err = proto.Marshal(execAsm)
resp(data, err)
}

```
func inProcExecuteAssemblyHandler(data []byte, resp RPCResponse) {
    execReq := &sliverpb.InvokeInProcExecuteAssemblyReq{}
    err := proto.Unmarshal(data, execReq)
    if err != nil {
        // {{if .Config.Debug}}
        log.Printf("error decoding message: %v", err)
        // {{end}}
        return
    }
    output, err := taskrunner.InProcExecuteAssembly(execReq.Data, execReq.Arguments, execReq.Runtime, execReq.AmsiBypass, execReq.EtwBypass)
    execAsm := &sliverpb.ExecuteAssembly{Output: []byte(output)}
    if err != nil {
        execAsm.Response = &commonpb.Response{
            Err: err.Error(),
        }
    }
    data, err = proto.Marshal(execAsm)
    resp(data, err)
}
```

It takes as input **data**, the serialized request, as an array of bytes, and **resp** corresponding to a **callback**.

The function **unserializes data in the struct InvokeInProcExecuteAssemblyReq** (this corresponds to the request sent by the server). Now the implant processes the request (the variable **execReq**) and calls taskrunner.InProcExecuteAssembly(), passing as input the parameters contained in execReq.

At this point, the implant performs the following operations:

- save the output inside a struct of type **sliverpb.ExecuteAssembly**, again defined in **sliver.proto**.
- serialize the struct.
- call the callback resp, passing as input the serialized struct.

The **callback resp** will **end up returning the serialized struct to the server**, **as a response to the initial request**, through the communication channel in use (that again could be HTTP/S, DNS, WireGuard, etc.).

At this point, on the server-side, the [rpc.GenericHandler()](https://github.com/BishopFox/sliver/blob/master/implant/sliver/handlers/handlers_windows.go) function receives the response, and returns it to [ExecuteAssembly()](https://github.com/BishopFox/sliver/blob/master/server/rpc/rpc-tasks.go#L127), which finally sends it back to the client through gRPC.

In the end, the client receives and processes the response, and prints data on screen for the operator.

By now you should have a basic understanding of the internals of Sliver. Be ready for the third and final part of this [series](https://hnsecurity.it/tag/sliver/)!

[c2](https://hnsecurity.it/blog/tag/c2/) [red teaming](https://hnsecurity.it/blog/tag/red-teaming/) [sliver](https://hnsecurity.it/blog/tag/sliver/) [golang](https://hnsecurity.it/blog/tag/golang/) [windows](https://hnsecurity.it/blog/tag/windows/)

[![](https://hnsecurity.it/wp-content/uploads/2025/09/BURP.jpg)](https://hnsecurity.it/blog/extending-burp-suite-for-fun-and-profit-the-montoya-way-part-9/?media_link=1)

[Tools](https://hnsecurity.it/blog/category/tools/)[Articles](https://hnsecurity.it/blog/category/articles/)

December 10, 2025

### [Extending Burp Suite for fun and profit – The Montoya way – Part 9](https://hnsecurity.it/blog/extending-burp-suite-for-fun-and-profit-the-montoya-way-part-9/)

[![Groovy logo](https://hnsecurity.it/wp-content/uploads/2025/09/GROOVY.jpg)](https://hnsecurity.it/blog/groovy-template-engine-exploitation-part-2/?media_link=1)

[Exploits](https://hnsecurity.it/blog/category/exploits/)[Articles](https://hnsecurity.it/blog/category/articles/)

November 11, 2025

### [Groovy Template Engine Exploitation – Notes from a real case scenario, part 2](https://hnsecurity.it/blog/groovy-template-engine-exploitation-part-2/)

[![Brida logo](https://hnsecurity.it/wp-content/uploads/2025/10/BRIDA_2.png)](https://hnsecurity.it/blog/brida-0-6-released/?media_link=1)

[Tools](https://hnsecurity.it/blog/category/tools/)[Articles](https://hnsecurity.it/blog/category/articles/)

October 28, 2025

### [Brida 0.6 released!](https://hnsecurity.it/blog/brida-0-6-released/)

[![hex-rays logo](https://hnsecurity.it/wp-content/uploads/2025/10/HEX-RAYS_4.png)](https://hnsecurity.it/blog/streamlining-vulnerability-research-with-the-idalib-rust-bindings-for-ida-9-2/?media_link=1)

[Articles](https://hnsecurity.it/blog/category/articles/)[Tools](https://hnsecurity.it/blog/category/tools/)

October 14, 2025

### [Streamlining Vulnerability Research with the idalib Rust Bindings for IDA 9.2](https://hnsecurity.it/blog/streamlining-vulnerability-research-with-the-idalib-rust-bindings-for-ida-9-2/)

[![LLM Icon](https://hnsecurity.it/wp-content/uploads/2025/09/LLM.jpg)](https://hnsecurity.it/blog/attacking-genai-applications-and-llms-sometimes-all-it-takes-is-to-ask-nicely/?media_link=1)

[Articles](https://hnsecurity.it/blog/category/articles/)

July 29, 2025

### [Attacking GenAI applications and LLMs – Sometimes all it takes is to ask nicely!](https://hnsecurity.it/blog/attacking-genai-applications-and-llms-sometimes-all-it-takes-is-to-ask-nicely/)

[![](https://hnsecurity.it/wp-content/uploads/2025/09/CIRCUITI.jpg)](https://hnsecurity.it/blog/fault-injection-follow-the-white-rabbit/?media_link=1)

[Articles](https://hnsecurity.it/blog/category/articles/)

June 18, 2025

### [Fault Injection – Follow the White Rabbit](https://hnsecurity.it/blog/fault-injection-follow-the-white-rabbit/)

[![ZeroDay logo](https://hnsecurity.it/wp-content/uploads/2025/09/ZERODAY.jpg)](https://hnsecurity.it/blog/my-zero-day-quest-bluehat-podcast/?media_link=1)

[Events](https://hnsecurity.it/blog/category/events/)[Vulnerabilities](https://hnsecurity.it/blog/category/vulnerabilities/)[Articles](https://hnsecurity.it/blog/category/articles/)

May 6, 2025

### [My Zero Day Quest & BlueHat Podcast](https://hnsecurity.it/blog/my-zero-day-quest-bluehat-podcast/)

[![Rust logo](https://hnsecurity.it/wp-content/uploads/2025/09/RUST.jpg)](https://hnsecurity.it/blog/aiding-reverse-engineering-with-rust-and-a-local-llm/?media_link=1)

[Tools](https://hnsecurity.it/blog/category/tools/)[Articles](https://hnsecurity.it/blog/category/articles/)

April 15, 2025

### [Aiding reverse engineering with Rust and a local LLM](https://hnsecurity.it/blog/aiding-reverse-engineering-with-rust-and-a-local-llm/)

[![Rust logo](https://hnsecurity.it/wp-content/uploads/2025/09/RUST.jpg)](https://hnsecurity.it/blog/streamlining-vulnerability-research-with-ida-pro-and-rust/?media_link=1)

[Tools](https://hnsecurity.it/blog/category/tools/)[Articles](https://hnsecurity.it/blog/category/articles/)

February 25, 2025

### [Streamlining vulnerability research with IDA Pro and Rust](https://hnsecurity.it/blog/streamlining-vulnerability-research-with-ida-pro-and-rust/)

[Scroll to top](https://hnsecurity.it/blog/customizing-sliver-part-2/#)

We use cookies to improve your browsing experience and analyze our traffic. By clicking "Accept all", you consent to the use of cookies.Accept AllPrivacy policy