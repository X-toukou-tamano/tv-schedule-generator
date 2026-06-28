import os
import zipfile


def create_zip(ppt_paths):

    upload_dir = os.path.join(
        os.getcwd(),
        "uploads"
    )

    zip_path = os.path.join(
        upload_dir,
        "場内放映予定.zip"
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as zf:

        for path in ppt_paths:

            zf.write(
                path,
                arcname=os.path.basename(path)
            )

    return zip_path
