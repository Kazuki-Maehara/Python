import pandas as pd
import sys
import os
from pathlib import Path
import datetime
import platform

RESULT_SWITCH = "By Resin"
# RESULT_SWITCH = "By Product Number"

dropColumns = [x for x in range(0, 11)]
for i in [4, 6, 7]:
    dropColumns.remove(i)

for i in range(20, 90, 20):
    for j in range(1, 11):
        dropColumns.append(i + j)

# Replaced
# dropColumns = [
#     0, 1, 2, 3, 5, 8, 9, 10,
#     21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
#     41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
#     61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
#     81, 82, 83, 84, 85, 86, 87, 88, 89, 90
# ]

df = pd.read_csv('./src/data.csv', encoding='shift-jis', header=None)
df = df[0:-1]

droppedDf = df.drop(columns=dropColumns)
droppedDf.columns = list(range(len(droppedDf.columns)))
droppedDf[2] = droppedDf[2].str[0:4]


sanitizedDf = pd.DataFrame(
    columns=[x for x in range(0, 5)]
)


for i in range(3, 60, 2):
    addingDf = pd.concat(
        [droppedDf[[0, 1, 2]],
         droppedDf[i],
         droppedDf[i+1]],
        axis=1,
        ignore_index=True
    )

    sanitizedDf = pd.concat(
         [sanitizedDf, addingDf],
         axis=0,
         ignore_index=True
         )

headedDf = sanitizedDf.rename(
    columns={
        0: "Product Number",
        1: "Product Name",
        2: "Model",
        3: "Date",
        4: "Quantity"
    }
)

headedDf["Date"] = headedDf["Date"].astype(str).str[0:6]
headedDf["Quantity"] = headedDf["Quantity"].astype(int)

resinDf = pd.read_csv('./src/resinMaster.csv', encoding='utf-8')

mergedDf = pd.merge(
    headedDf,
    resinDf,
    on=[
        "Product Number",
        "Product Name"
    ],
    how='left'
)

# mergedDf = mergedDf.fillna(0)


mergedDf["Consumption"] = mergedDf["Quantity"] * mergedDf["Unit Mass"]

calculatedDf = mergedDf.drop(columns=["Unit Mass", "Quantity"])


if (RESULT_SWITCH == "By Product Number"):
    finishedDf = calculatedDf.pivot_table(
        values="Consumption",
        index=["Model", "Product Number", "Product Name", "Resin"],
        columns="Date"
    )

elif (RESULT_SWITCH == "By Resin"):
    finishedDf = calculatedDf.pivot_table(
        values="Consumption",
        index=["Resin"],
        columns="Date"
    )


headedDf.to_csv(
    "./output/sanitized.csv",
    header=True,
    index=True,
    encoding="utf-8"
)

finishedDf.to_csv(
    "./output/pivot.csv",
    header=True,
    index=True,
    encoding="utf-8"
)

# ----- For dislaying infomation -----
print("\n" * 3)
print(
    "Run at: ",
    datetime.datetime.now()
)
print(
    "Data Source: ",
    os.path.basename(Path(sys.argv[1])), "\n",
    "\tSize: ", os.path.getsize(Path(sys.argv[1])), "bytes", "\n",
    "\tModified: ", datetime.datetime.fromtimestamp(
        os.path.getmtime(Path(sys.argv[1]))), "\n",
    "\tCreated: ", datetime.datetime.fromtimestamp(
        os.path.getctime(Path(sys.argv[1]))),
)
print(
    "Powered By : Python ",
    sys.version.replace("\n", " " * 1)
)
print(
    "Platform: ",
    platform.platform()
    )
print("-" * 80)
print(finishedDf)
print("-" * 80)
