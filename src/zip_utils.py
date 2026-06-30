import os
import zipfile
from io import BytesIO


def create_zip(ppt_paths):

    zip_buffer = BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as zf:

        for path in ppt_paths:

            zf.write(
                path,
                arcname=os.path.basename(path)
            )

    # ZIP作成後、元のPPTを削除
    for path in ppt_paths:
        if os.path.exists(path):
            os.remove(path)

    zip_buffer.seek(0)

    return zip_buffer.getvalue()
