import pandas as pd

before_data = pd.read_csv("MOCK_DATA.csv")
after_data = pd.read_csv("MOCK_DATA_2.csv")

# Set the primary key column
primary_field = 'id'

# Set the other field to test for differences
other_field = 'ip_address'

pk_before = before_data[primary_field].astype(str)
pk_after = after_data[primary_field].astype(str)
count_b, count_a = len(pk_before), len(pk_after)

other_field_before = before_data[other_field].astype(str)
other_field_after = after_data[other_field].astype(str)

dict_before, dict_after = {}, {}

for i, exc in enumerate(pk_before):
    dict_before[exc] = other_field_before[i]

for i, exc in enumerate(pk_after):
    dict_after[exc] = other_field_after[i]

# Get newly found and completely lost rows
new = list(set(pk_after) - set(pk_before))
new2 = [x+' : '+dict_after[x] for x in new]
lost = list(set(pk_before) - set(pk_after))
lost2 = [x+' : '+dict_before[x] for x in lost]

# Get changes in other field in rows
changes = {x: dict_before[x]+"  ->  "+dict_after[x] for x in dict_after if x in dict_before and dict_after[x] != dict_before[x]}

# Print to sdtout
print("New rows : "+str(len(new))+" - total: "+str(count_a))
print(','.join(new))
[print(x) for x in new2]
print()
print("Rows lost : "+str(len(lost))+" - total: "+str(count_b))
print(','.join(lost))
[print(x) for x in lost2]
print()
print("Changes in "+ other_field_before.name +" field: "+str(len(changes)))
[print(key+' : '+value) for key, value in changes.items()]

# Write to output file
with open('changes_csv.txt', 'w') as f:
    f.write("New rows in "+pk_before.name+" : "+str(len(new))+" - total: "+str(count_a)+'\n')
    f.write(','.join(new)+'\n')
    [f.write(x+'\n') for x in new2]
    f.write('\n')
    f.write("Rows lost in "+ pk_before.name +" : "+str(len(lost))+"- total: "+str(count_b)+'\n')
    f.write(','.join(lost)+'\n')
    [f.write(x+'\n') for x in lost2]
    f.write('\n')

    f.write("Changes in "+ other_field_before.name +" field: "+str(len(changes))+'\n')
    [f.write(key+' : '+value+'\n') for key, value in changes.items()]

    f.close()