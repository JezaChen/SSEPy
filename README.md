# SSEPy: Implementation of searchable symmetric encryption in pure Python

Searchable symmetric encryption, one of the research hotspots in applied cryptography, has continued to be studied for two decades. A number of excellent SSE schemes have emerged, enriching functionality and optimizing performance. However, many SSE schemes have not been implemented concretely and are generally stuck in the prototype implementation stage, and worse, most SSE schemes are not publicly available in source code. Based on this foundation, this project first implements SSE schemes (first single-keyword, then multi-keyword) published in top conferences and journals, and then implements them into concrete applications. I hope that this project will provide a good aid for researchers as well as a reference for industry.

This is a project that is moving forward...

## Implemented schemes

### Single-keyword Static SSE Schemes

- (Completed) SSE-1 and SSE-2 in \[CGKO06\]: Curtmola, Reza, et al. "Searchable symmetric encryption: improved definitions and efficient constructions." Proceedings of the 13th ACM conference on Computer and communications security. 2006.
- (Completed) Schemes PiBas, PiPack, PiPtr and Pi2Lev in \[CJJ+14\]: Cash, David, et al. "Dynamic Searchable Encryption in Very-Large Databases: Data Structures and Implementation." (2014).
- (Completed) Scheme Pi in \[CT14\]: Cash, David, and Stefano Tessaro. "The locality of searchable symmetric encryption." Annual international conference on the theory and applications of cryptographic techniques. Springer, Berlin, Heidelberg, 2014.
- (Completed) Scheme 3 (Section 5, Construction 5.1) in \[ANSS16\]: Asharov, Gilad, et al. "Searchable symmetric encryption: optimal locality in linear space via two-dimensional balanced allocations." Proceedings of the forty-eighth annual ACM symposium on Theory of Computing. 2016.
