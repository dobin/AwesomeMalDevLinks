# https://blog.barthe.ph/2009/02/22/change-signed-executable/

It should not be possible, but it is… sort of.

## How it Works

Microsoft Authenticode works as follows: it computes a cryptographic hash of the executable file. The hash is then used to make a digital certificate which is authenticated by some trusted authority.

The certificate is attached to the end of the PE executable, in a dedicated section called the Certificate Table. When the executable is loaded, Windows computes the hash value, and compares it to the one attached to the Certificate table. It should “normally” be impossible to change anything in the file without breaking the digital authentication.

However three areas of a PE executable are excluded from the hash computation:

- the Checksum in the optional Windows specific header: 4 bytes.
- the Certificate Table entry in the optional Windows specific header: 8 bytes.
- the Digital Certificate section at the end of the file: variable length.

You should be able to change those area without breaking the signature. I have discovered by accident that it is possible to append an arbitrary amount of data at the end of the Digital Certificate. The data are ignored by both the signature parsing and hash computation algorithms. It works on all version of Windows I tested (2000, XP, Vista), as long as the length of the Certificate Table is correctly increased. The length is stored in two different location: the PE header and the beginning of the certificate table.

## How to Add a Payload to a Signed Executable

1. Locate beginning of PE header (`PE`)
2. Skip COFF header (+=28 bytes)
3. Go to Certification Table Entry in the Windows specific optional PE header (+=120 bytes after COFF; total +=148 bytes)
4. Change size of Certificate Table as defined in `IMAGE_DATA_DIRECTORY.Size` to add the size of the payload.
5. Go to location defined `IMAGE_DATA_DIRECTORY.VirtualAddress`. This is the absolute location of the Certificate Table within the file.
6. Change again the size of the header, inside the `PKCS1_MODULE_SIGN.dwLength`
7. This should normally be the last section in the executable; so go to the end and add payload
8. Possibly calculate the new checksum of the file

**Caution**: the previous constants are true for the 32 bit x86 versions of Windows. Payload needs to be 64 bits aligned. All the 32 bits constants are of course little endians woo woo!

## Documentation Links

- [http://www.thehackerslibrary.com/?p=377](https://web.archive.org/web/20090219224404/http://www.thehackerslibrary.com/?p=377)
- [http://msdn.microsoft.com/en-us/library/ms904424.aspx](http://msdn.microsoft.com/en-us/library/ms904424.aspx)
- [http://msdn.microsoft.com/en-us/library/aa448396.aspx](http://msdn.microsoft.com/en-us/library/aa448396.aspx)

## Sources

- [AppendPayLoad.tar.bz2](https://blog.barthe.ph/download/2009/AppendPayLoad.tar.bz2)

* * *