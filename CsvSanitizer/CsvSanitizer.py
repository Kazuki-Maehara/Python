import pandas as pd

dropColumns = [
    0, 1, 2, 3, 5, 8, 9, 10,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    81, 82, 83, 84, 85, 86, 87, 88, 89, 90
]

df = pd.read_csv('./src/data.csv', encoding='shift-jis', header=None)
df = df[0:-1]

droppedDf = df.drop(columns=dropColumns)
droppedDf.columns = list(range(len(droppedDf.columns)))
droppedDf[2] = droppedDf[2].str[0:4]


sanitizedDf = pd.concat(
    [droppedDf[[0, 1, 2]],
     droppedDf[3],
     droppedDf[4]],
    axis=1
)

for i in range(5, 60, 2):
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


# pivotDf = headedDf.pivot_table(
#     values="Quantity",
#     index=["Model", "Product Number", "Product Name"],
#     columns="Date"
# )
#
# finishedDf = pivotDf

finishedDf = headedDf

print(finishedDf)

finishedDf.to_csv(
    "./output/sanitized.csv",
    header=True,
    index=True,
    index_label="id",
    encoding="utf-8"
)
