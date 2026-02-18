# https://sabotagesec.com/reflection-in-c-101/

[Skip to content](https://sabotagesec.com/reflection-in-c-101/#wp--skip-link--target)

## Reflection in C\# 101

## Background

As someone who is engaged in cyber threat intelligence, one needs to keep track of novel techniques employed by the adversaries to deliver their payload on to the target systems without having to touch the filesystem at all, completely fileless deployment, thus bypassing baseline detection mechanisms. As a means to achieve fileless delivery, malware authors are extensively using programmatic features in PowerShell and C#, to be specific none other than **reflection**. As a security researcher, one should know of such powerful features. In this blog post we will dive into basic concept of reflection through few code samples.

Reflection in the wild: Use Cases

- Malware stager application will contain an assembly stored in the byte array, it will get dynamically loaded into memory and specific methods will get invoked via reflection. The assembly can be either a final payload like commodity RAT/custom beacon or another stager.
- Some advanced use case of reflection is creation of an assembly on the fly in the memory to house a payload and eventually creating an invoke method using delegates to map the function prototype with the invoke method of the created assembly.

\[Not Covered in this article, may be a future post 🙂 \]

Even types having access modifiers like internal or private can be accessed individually via reflection.

## Objective

- I will give you a very intuitive explanation for reflection without copy-pasting what MSDN has to say about it, nevertheless will share appropriate MSDN documentation links.
- We will see how to create a simple and basic DLL assembly in C# using Visual Studio 2019 Community edition.
- We will code a loader in C# to reflectively load assembly\[DLL\] at the runtime.

## **Reflection**: An Intuitive Approach

Before going head down into reflection, we need to know some literature in .NET universe. Following are few key terms that we need to understand:

**Common Language Runtime** \[CLR\]

CLR is to .NET as JVM is to Java, CLR can be seen as intermediate entity sits in between your machine and language to make the system more portable and independent of underlying hardware architecture. CLR converts .NET compliant code into an intermediate form called MSIL, similar to Bytecode in Java. More on .NET implementation can be found [here](https://sabotagesec.com/%22https://docs.microsoft.com/en-us/dotnet/standard/clr/%22).

**Managed** vs **Unmanaged Code**

Any code which is compliant to .NET is under the control of memory management of CLR, such code a code is termed as managed piece of code. Likewise code which is not under the control of the CLR\\’s memory management is generally termed as un-managed code.

**Assembly**

In .NET literature, an assembly can be either a managed executable or a managed Dynamic Link Library. An assembly will have a manifest containing the metadata of the code which plays a major role in reflection.

**World of reflection**

**Reflection** is mainly a technique employed at runtime to dynamically get metadata of loaded assemblies in the memory. In C# it is not just about getting the data, reflection lets us create objects and bind them to Types\[classes\] obtained at runtime, thus allowing us to access the methods and properties within such Types leading to invocation and computation on Type members. **System.Reflection** namespace has so many classes that can be used to load, investigate and load assemblies. Important classes in the namespace:

- [Assembly](https://sabotagesec.com/%22https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assembly?view=net-5.0\%22) Loading/investigation/manipulation of an assembly
- [AssemblyName](https://sabotagesec.com/%22https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assemblyname?view=net-5.0\%22) To explore assembly details
- [EventInfo](https://sabotagesec.com/%22https://docs.microsoft.com/en-us/dotnet/api/system.reflection.eventinfo?view=net-5.0\%22) Event information
- [PropertyInfo](https://sabotagesec.com/%22https://docs.microsoft.com/en-us/dotnet/api/system.reflection.propertyinfo?view=net-5.0\%22) Holds information of properties in a Type
- [MethodInfo](https://sabotagesec.com/%22https://docs.microsoft.com/en-us/dotnet/api/system.reflection.methodinfo?view=net-5.0\%22) Holds information of methods in a Type

Reflection: Basic Implementation Steps

Our goal is to load a custom assembly, call a method defined inside it using reflection. Types mentioned in the following steps are part of the System.Reflection namespace.

- **_Load your desired assembly code_**. Loading can be done in various ways depending on the situation. We need to use the Assembly Type. Refer to [documentation](https://sabotagesec.com/%22https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assembly?view=net-5.0\%22) to know more about various loading methods to load assembly in the memory.
- **_Get the Type information from the loaded assembly_**. Type information can be extracted by using GetType() in Assembly class. This method returns a Type, thus we can store the type information in a Type object to later use it to instantiate the specific type in the assembly.
- **_Instantiate the Type_**. In this step we will create an object for the specified Type in the assembly. Using this object we can access its members \[properties and methods\].
- **_Get method information_**. Using MethodInfo class we can get methods from within the assembly using type object created in the step 2. We need to create a MethodInfo object to hold target method information.
- _**Invoke the method**._ MethodInfo class has a method called Invoke which is overloaded. We will use the Invoke method on MethodInfo object created in the step 4 to call the method.

## Reflection: Coding DLL & Loader

**A Simple DLL**

DLL is nothing but a code repository from which we can use methods using appropriate namespace to carry out computations on data.

Fire up your Visual Studio IDE, I am using 2019 community edition. A C#/.NET DLL is simply types \[classes\] defined within a namespace. These types can host variety of methods and properties depending on the functionality and usage. Our DLL logic will be very basic and trivial, just write something to console output!!

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11 | `using``system``;`<br>`namespace``Test_Library`<br>`{`<br>```class``Test`<br>```{`<br>```public``void``Method()`<br>```{`<br>```Console.WriteLine(\"Method Invoked\");`<br>```}`<br>```}`<br>`}` |

There are many resource on DLL creation in Visual Studio. Now we are good to build our solution, keep in mind use ANY CPU build configuration to make things simple. 🙂

Default build directory is : **_C:\\\Users\\\<user\_name>\\\source\\\repos\\\_**

Keep in mind fully qualified name of the method will be : **Test\_Library.Test.Method()**

Now a dll file will be present in the bin folder of your build directory. Now we are done with dll creation. Lets create a loader!!

**Loader**

Loader will be a console application, take appropriate steps to create a Visual Studio solution.

We will be following basic implementation steps discussed above to code our loader.

**_Load your desired assembly code_**

|     |     |
| --- | --- |
| 1 | `Assembly asm = Assembly.LoadFile(@\"dll\\location\\Test_Library.dll\");` |

We are creating an object of type Assembly to hold the loaded assembly. Entire dll assembly can be referenced via asm object.

**_Get the Type information from the loaded assembly_**

|     |     |
| --- | --- |
| 1 | `Type t = asm.GetType(\"Test_Library.Test\");` |

We are storing the Type information into object t of type Type. GetType() is a method in Assembly class. Test\_Library.Test is the type we are interested in. Keep in mind, an assembly can have any number of classes. In next step we can use this type information to create an object of it.

**_Instantiate_****_the Type_**

|     |     |
| --- | --- |
| 1 | `object obj = Activator.CreateInstance(t);` |

Activator type can be used to create an object of Type given as the argument. Object is stored in variable obj of type Object. The type provided is of Test\_Library.Test in the assembly. Now we can access type members in the assembly via obj.

_**Get method information**_

|     |     |
| --- | --- |
| 1 | `MethodInfo meth = t.GetMethod(\"Method\");` |

Since we know in and out of the loaded assembly, which is the case in most of the malware code because malware author knows what he is doing 😉 . Using the type t defined previously, we can use GetMethod on it to retrieve the method information and store it in object meth of type MethodInfo.

_**Invoke the method**_

|     |     |
| --- | --- |
| 1 | `meth.Invoke(obj, null);` |

We can use Invoke on MethodInfo object to finally call the method at runtime. Invoke method is an overloaded method, please refer to [documentation](https://sabotagesec.com/%22https://docs.microsoft.com/en-us/dotnet/api/system.reflection.methodbase.invoke?view=net-5.0#:~:text=To%20invoke%20a%20static%20method,The%20return%20value%20is%20null%20.\%22). Invoke takes two arguments, one is object by which we need to make the call and second argument is array of arguments passed to the invoked method.

In our case, first argument is obj, which is the object of type Test\_Library.Test, second argument is null because our method has no defined parameters, therefore it takes no arguments.

Output

![\"\"](https://sabotagesec.com/wp-content/uploads/2021/05/image.png?w=317\%22)

Complete Code

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31 | `using``System;`<br>`using``System;`<br>`using``System.Reflection;`<br>`namespace``ConsoleProgram`<br>`{`<br>```class``Program`<br>```{`<br>```static``void``Main(string[] args)`<br>```{`<br>``<br>```Assembly asm = Assembly.LoadFile(@\"path\\to\\dll\");`<br>```try`<br>```{`<br>```Type t = asm.GetType(\"Test_Library\");`<br>```object obj = Activator.CreateInstance(t);`<br>```MethodInfo meth = t.GetMethod(\"Method\");`<br>```meth.Invoke(obj, null);`<br>```}`<br>```catch``(ReflectionTypeLoadException ex)`<br>```{`<br>```Console.WriteLine(\"Inside Catch..\");`<br>```Exception[] Exceptions = ex.LoaderExceptions;`<br>```foreach (Exception curEx in Exceptions)`<br>```{`<br>```string curMessage = curEx.Message;`<br>```Console.WriteLine(\"Message:{0}\", curMessage);`<br>```}`<br>```}`<br>```}`<br>```}`<br>`}` |

For beginners, don\\’t worry about nightmare in the catch statement, it is to catch error while loading the assembly, if something goes wrong while loading, it will give us better debugging options.

Now we know basics of reflection, in the next post I will be using the same resources but assembly will be stored within the loader program as a byte array which is the case in many malwares, then we will load the assembly as a byte array.

Till then,

CHEERIOS 🙂

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

### One response to “Reflection in C\# 101”

1. [Assembly Byte Embedding & Reflection – offensivecraft](https://offensivecraft.wordpress.com/2021/05/26/assembly-byte-embedding-reflection/)





[May 26, 2021 at 3:09 am](https://sabotagesec.com/reflection-in-c-101/#comment-2)











\[…\] is a follow up writing to my previous article on basics of reflection. It is very common to see an encoded/encrypted/archived payload stored \[…\]





[Reply](https://sabotagesec.com/reflection-in-c-101/?replytocom=2#respond)


### Leave a Reply [Cancel reply](https://sabotagesec.com/reflection-in-c-101/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.