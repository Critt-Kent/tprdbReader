import pandas as pd
import glob
from google.cloud import storage
import io


def readTPRDBtables(studies, ext, user = "TPRDB", path = "/data/critt/tprdb/", verbose = 0):
    """
    Read data Tables from the TPR-DB 
    # Parameters:
        studies: list of studies, e.g., ['BML12', 'SG12', 'AR22']
        ext: type of table, one of {ss, sg, st, tt, kd, fd, au, pu, hof, pol}
        user: USER (default TPRDB)
        verbose: when 
    Return: Dataframe of concatenated tables for all sessions in all studies 
    """
    df = pd.DataFrame()
    for study in studies:
        files = glob.glob(f"{path}/{user}/{study}/Tables/*{ext}")
        if(verbose): print(f"Reading:{study}\twith {len(files)} '{ext}' Tables")
        for fn in files:
            if(verbose> 1): print(f"\t{fn}")
            df = pd.concat([df, pd.read_csv(fn, sep="\t", dtype=None)], ignore_index=True)
        
    if(verbose): print(f"Total '{ext}' data rows:{df.shape[0]}, columns:{df.shape[1]}")
    return(df)



def readTPRDBtable_GCP(studies, ext, user="TPRDB", verbose=0):
    """
    Reads files from a Google Cloud Storage bucket that match the specified extension,
    constructing the path as:
      data/critt/tprdb/<user>/<study>/Tables/
      
    Parameters:
      studies (list): A list of study identifiers, e.g. ["ACS08", "AR20"].
                      The function will append "/Tables/" to each study.
      ext (str): File extension pattern, e.g. "kd" (files ending with this string).
      user (str): A folder name under the base path. Default is "TPRDB".
      verbose (int): If non-zero, prints the number of sessions and rows processed.
      
    Returns:
      A pandas DataFrame containing the concatenated data from the matching files.
    """
    # Hard-code the bucket name and base path
    bucket_name = "crittdata"
    base_path = "data/critt/tprdb/"  # no leading slash for Cloud Storage object names

    # Construct the full base path using the user parameter.
    # For example, if user is "TPRDB", then final_base = "data/critt/tprdb/TPRDB/"
    final_base = f"{base_path}{user.strip('/')}/"

    # Initialize an anonymous client
    client = storage.Client.create_anonymous_client()

    # Get a bucket reference
    bucket = client.bucket(bucket_name)

    df = pd.DataFrame()

    for study in studies:
        # Build the full prefix:
        # For each study, add "/Tables/" after the study name.
        # For example, if study is "ACS08", prefix becomes:
        # "data/critt/tprdb/TPRDB/ACS08/Tables/"
        study_folder = f"{study.strip('/')}/Tables/"
        prefix = f"{final_base}{study_folder}"

        # List all blobs (files) under the constructed prefix.
        blobs = bucket.list_blobs(prefix=prefix)

        if not ext.startswith('.'):
            ext = '.' + ext

        # Filter the blobs by file extension.
        files = [blob.name for blob in blobs if blob.name.endswith(ext)]

        if not files:
            print(f"No files found for study {study} with extension {ext}")
            continue

        # Download file content and load each into a DataFrame.
        dataframes = []
        for file in files:
            blob = bucket.blob(file)
            content = blob.download_as_text()  # Download the content as text
            dataframes.append(pd.read_csv(io.StringIO(content), sep="\t"))

        # Print summary information if verbose.
        if verbose:
            row_count = sum(len(df_temp.index) for df_temp in dataframes)
            print(f"{study}\t#sessions: {len(dataframes)}\t{ext}:{row_count}")

        # Combine current study's DataFrames with the cumulative DataFrame.
        dataframes.insert(0, df)
        df = pd.concat(dataframes, ignore_index=True)

    return df

