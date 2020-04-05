# tot-ocr

ToT service responsible for generating OCR resources from PDF files and gerate
their _searchable_ variant. OCR files will be stored in a _tot-ocr_ bucket and
searchable files will be stored in a _tot-searchable_ bucket.

This service runs within a Docker container, which listens (for now) to _Minio_
events when a new PDF file is stored in the _tot-pdf_ bucket. _Minio_ is an
object storage facility while Openstack is not ready yet.

### Usage

For testing purposes you can start a _Minio_ instance with (from within this
project's directory):

```sh
./bin/start-minio.sh
```

This scripts runs a _Minio_ instance with _Docker_ and default credentials
"minioadmin:minioadmin" and address defaulted to "localhots:9000". Change
credentials and desired port mappings in the script if you want.

Once _Minio_ instance is started you can access `http://localhost:9000` to see
its browser interface. You can interact with buckets and objects in the
interface or start using any clients you want: _Go_, _Python_, _Java_ or it's
own _CLI_.

This project also provides a helper script which uploads a given file to _Minio_,
but it is intended to use for debbuging purposes only.

In order to start developing you can use the `./bin/setup-tot.py` script to
create the required resources to use during development.
