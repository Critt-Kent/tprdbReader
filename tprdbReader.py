import pandas as pd
import glob


# Read data Tables from the TPR-DB 
# Parameters:
# studies: list of studies, e.g., ['BML12', 'SG12', 'AR22']
# ext: type of table, one of {ss, sg, st, tt, kd, fd, au, pu, hof, pol}
# user: USER (default TPRDB)
# verbose: when 
# Return: Dataframe of concatenated tables for all sessions in all studies 

def readTPRDBtables(studies, ext, user = "TPRDB", path = "/data/critt/tprdb/", verbose = 0):
    df = pd.DataFrame()
    for study in studies:
        files = glob.glob(f"{path}/{user}/{study}/Tables/*{ext}")
        if(verbose): print(f"Reading:{study}\twith {len(files)} '{ext}' Tables")
        for fn in files:
            if(verbose> 1): print(f"\t{fn}")
            df = pd.concat([df, pd.read_csv(fn, sep="\t", dtype=None)], ignore_index=True)
        
    if(verbose): print(f"Total '{ext}' data rows:{df.shape[0]}, columns:{df.shape[1]}")
    return(df)

