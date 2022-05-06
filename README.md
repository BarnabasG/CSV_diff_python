# CSV/XLSX diff tool - python
### A simple diff tool for comparing two CSV or Excel files in python

Select the files to compare and press load to load the data

![image](https://user-images.githubusercontent.com/57625180/164936735-2aacc0ef-ab04-4995-911d-b11205675c84.png)

Select the primary fields and any fields to ignore, as well as whether to write the results to a text file

![image](https://user-images.githubusercontent.com/57625180/164936965-f69ce857-8d12-4109-8e8d-d4e8aa97c962.png)

A difference summary is shown

![image](https://user-images.githubusercontent.com/57625180/164937132-c4aa76f4-b2e1-4a9d-8731-be2775b9da4a.png)

There is one duplicate primary key. Duplicate key's should be 0 or some differences cannot be calculated accurately

![image](https://user-images.githubusercontent.com/57625180/164937258-9d397605-b163-4b26-8b57-cb3c795cef21.png)

The changes are shown

![image](https://user-images.githubusercontent.com/57625180/164937471-690bbb17-5a08-42b4-ad0c-6363299364e5.png)

This can be filtered by field

![image](https://user-images.githubusercontent.com/57625180/164937803-19fb4060-0b66-4c42-806b-9795aa59035d.png)

All of these 'New Rows' are present in the second file but not the first file (by primary fields)

![image](https://user-images.githubusercontent.com/57625180/164937991-9e63194e-243e-4435-9da8-7b9b7181ea6e.png)

The 'Rows Lost' are preset in the first file but not the second

![image](https://user-images.githubusercontent.com/57625180/164938166-a8969938-ec89-4571-b0f8-2e6e461be8fe.png)

The data can be viewed and queried

![image](https://user-images.githubusercontent.com/57625180/164940308-c1857fe5-4a0b-40e6-bf26-984af6e05fdb.png)

![image](https://user-images.githubusercontent.com/57625180/164938688-48768118-4ccb-4f5c-bd4b-38c905976373.png)

## Limitations

The contents of the files are loaded into a pandas dataframe before any processing can occur. For larger datasets, CSV files show a large performance increase over XLSX/XLS files.
After data is loaded, running comparissons is significantly less time consuming.

