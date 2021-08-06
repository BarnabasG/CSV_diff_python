import pandas as pd

# Set the 2 csv files to compare
before_data = pd.read_csv("MOCK_DATA.csv")
after_data = pd.read_csv("MOCK_DATA_2.csv")

# Set the primary key column
primary_field = 'id'

# All other columns set for comparisson by default
other_fields = [x for x in list(before_data.columns) if x != primary_field]

# Or use this like to select specific columns to compare
#other_fields = ["ip_address", "email","last_name","gender"]


pk_before = before_data[primary_field].astype(str)
pk_after = after_data[primary_field].astype(str)
count_b, count_a = len(pk_before), len(pk_after)

other_fields_before, other_fields_after = [], []

for field in other_fields:
    other_fields_before.append(before_data[field].astype(str))
    other_fields_after.append(after_data[field].astype(str))

dict_before, dict_after = {}, {}

for i, exc in enumerate(pk_before):
    dict_before[exc] = [x[i] for x in other_fields_before]

for i, exc in enumerate(pk_after):
    dict_after[exc] = [x[i] for x in other_fields_after]

# Get newly found and completely lost rows
new = list(set(pk_after) - set(pk_before))
new2 = [x+' : '+str(dict_after[x]) for x in new]
lost = list(set(pk_before) - set(pk_after))
lost2 = [x+' : '+str(dict_before[x]) for x in lost]

# Get changes in specific fields in rows
changes = {}
for key in dict_after:
    if key in dict_before:
        for i, val in enumerate(dict_after[key]):
            if val != dict_before[key][i]:
                add = other_fields[i]+" : "+str(dict_before[key][i])+"  ->  "+val
                if key in changes:
                    changes[key].append(add)
                else:
                    changes[key] = [add]

# Print to sdtout
print("New rows : "+str(len(new))+" - total: "+str(count_a))
print(','.join(new))
[print(x) for x in new2]
print()
print("Rows lost : "+str(len(lost))+" - total: "+str(count_b))
print(','.join(lost))
[print(x) for x in lost2]
print()
print("Changes : "+str(len(changes)))
[print(key+' : '+str(value)) for key, value in changes.items()]

# Write to output file
with open('changes_multi_col.txt', 'w') as f:
    f.write("New rows : "+str(len(new))+" - total: "+str(count_a)+'\n')
    f.write(','.join(new)+'\n')
    [f.write(x+'\n') for x in new2]
    f.write('\n')
    f.write("Rows lost : "+str(len(lost))+" - total: "+str(count_b)+'\n')
    f.write(','.join(lost)+'\n')
    [f.write(x+'\n') for x in lost2]
    f.write('\n')

    f.write("Changes : "+str(len(changes))+'\n')
    [f.write(key+' : '+str(value)+'\n') for key, value in changes.items()]

    f.close()