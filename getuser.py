from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from typing import Annotated
import json



app = FastAPI()

# This is User one ------------------>



def load_data_from_getuserjson():
    try:
        with open("getuserjson.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def save_data_to_getuserjson(data):
    with open("getuserjson.json","w") as f:
        json.dump(data,f,indent=4)

class UserData(BaseModel):
    itemName : Annotated[str,Field(...,description="Item Name")]
    quantity : Annotated[int,Field(...,description="Quantity")]
    date : Annotated[str,Field(...,description="Enter date in format dd/MM/yyyy",examples=["08/09/2025"])]
    itemBrand : Annotated[str,Field(...,description="Enter Buiscuit Name",examples=["Bourban,Oreo"])]
    employeeid : Annotated[int,Field(...,description="Enter employee ID",examples=[10111])]
    consumedPersonName : Annotated[str,Field(...,description="Enter person name",examples=["Vijay"])]

@app.post("/create/consumptiondata/")
def consumption_data(userdata : UserData):
    create_data = userdata.model_dump()
    existing_data = load_data_from_getuserjson()

    itemnameUser = userdata.itemName
    itembrandUser = userdata.itemBrand
    quantityUser = userdata.quantity
    existing_data_admin = load_data_from_getadminjson()
    for record in existing_data_admin:
        flag = 0
        if(record["itemName"] == itemnameUser and record["itemBrand"] == itembrandUser):
            flag = 1
            total = record["totalQuantity"]
            record["totalQuantity"] = record["totalQuantity"] - quantityUser
            if(record["totalQuantity"] < 0):
                return {f"message" : f"Remaining items are : {total}"}
            save_data_to_getadminjson(existing_data_admin)
           
    if flag == 0:
            return JSONResponse(status_code=404,content={"message" : "Item Name or Brand Name is not in admin."})
    existing_data.append(create_data)
    save_data_to_getuserjson(existing_data)
    return JSONResponse(status_code=200,content={"message":"Data Added Successfully!"})

@app.get("/consumptionData/getAllData")
def getAllConsumptionData():
    existing_data = load_data_from_getuserjson()
    return existing_data

@app.get("/consumptionData/getAllData/DateString/")
def getUserDataByDate(date : str):
    existing_data = load_data_from_getuserjson()
    flag = 0
    list_output = []
    for record in existing_data:
        if record["date"] == date:
            flag = 1
            list_output.append(record)
    if flag == 0:
        return JSONResponse(status_code=404, content={"message" : f"There is no data of {date}"})
    
    return list_output

@app.post("/consumptionData/getAllData/{employee_id}")
def getEmployeeConsumptionData(employee_id : int):
    output_data = []
    existing_data = load_data_from_getuserjson()
    for i in existing_data:
        if i["employeeid"] == employee_id:
            output_data.append(i)
    return output_data

@app.delete("/delete/data/consumption/")
def delete_particular_data(userData : UserData):
    existing_data = load_data_from_getuserjson()
    existing_admin_data = load_data_from_getadminjson()

    for i,value in enumerate(existing_data):
        if (value["itemName"] == userData.itemName and value["quantity"] == userData.quantity and value["date"] == userData.date and value["itemBrand"] == userData.itemBrand and value["employeeid"] == userData.employeeid):
            itemnameUser = userData.itemName
            itembrandUser = userData.itemBrand
            quantity = userData.quantity

            for record in existing_admin_data:
                if(record["itemName"] == itemnameUser and record["itemBrand"] == itembrandUser):
                    record["totalQuantity"] = record["totalQuantity"] + quantity
                    save_data_to_getadminjson(existing_admin_data)
                    break

            existing_data.pop(i)
            save_data_to_getuserjson(existing_data)
            return JSONResponse(status_code=200,content={"message" : "Record Deleted SuccessFully."})

    return JSONResponse(status_code=404,content="Record Not Found!")

@app.put("/update/data/consumption")
def update_consumption_data(itemname : str , _quantity : int , _date : str , itembrand : str , empid : int , consumedperson : str , userData : UserData):
    existing_data = load_data_from_getuserjson()
    existing_admin_data = load_data_from_getadminjson()
    new_data = userData.model_dump()
    for i,record in enumerate(existing_data):
        if (record["itemName"] == itemname and record["quantity"] == _quantity and record["date"] == _date and record["itemBrand"] == itembrand and record["employeeid"] == empid and record["consumedPersonName"] == consumedperson):
            itemnameUser = itemname
            itembrandUser = itembrand
            quantityUser = _quantity
            flag = 0
            for record in existing_admin_data:
                if(record["itemName"] == itemnameUser and record["itemBrand"] == itembrandUser):
                    record["totalQuantity"] = record["totalQuantity"] + quantityUser - userData.quantity
                    flag = 1
                    save_data_to_getadminjson(existing_admin_data)
                    break
            if flag == 0:
                return JSONResponse(status_code=404,content={"message" : "ItemName and Item brand is not in admin."})
            existing_data[i] = new_data
            save_data_to_getuserjson(existing_data)
            return JSONResponse(status_code=200,content={"message" : "Data Updated Successfully!"})
    return JSONResponse(status_code=404,content="Data Not Found!")






# This is Admin one ----------------------->




def load_data_from_getadminjson():
    try:
        with open("getadminjson.json","r") as f:
            data = json.load(f)
            return data
    except(FileNotFoundError,json.JSONDecodeError):
        return []

def save_data_to_getadminjson(data):
    with open("getadminjson.json","w") as f:
        json.dump(data,f,indent=4)

class AdminData(BaseModel):
    itemName : Annotated[str,Field(...,description="Item Name")]
    totalQuantity : Annotated[int,Field(...,description="Total Quantity")]
    date : Annotated[str,Field(...,description="Date")]
    itemBrand : Annotated[str,Field(...,description="Item Brand")]
    cost : Annotated[float,Field(...,description="Cost")]
    boughtPersonName : Annotated[str,Field(...,description="Bought Person Name")]

@app.post("/create/buyItem")
def bought_item(adminData : AdminData):
    existing_data = load_data_from_getadminjson()
    new_data = adminData.model_dump()

    existing_data.append(new_data)

    save_data_to_getadminjson(existing_data)

    return {"status" : "Item Added SuccessFully!"}

@app.get("/get/all/buyingItem")
def getAllBuyingItem():
    return load_data_from_getadminjson()

@app.get("/get/particular/itemName/{itemname}")
def get_particular_itemName(item_name : str):
    existing_data = load_data_from_getadminjson()
    flag = 0
    itemNameList = []
    for i,record in enumerate(existing_data):
        if(record["itemName"] == item_name):
            flag = 1
            itemNameList.append(record)
    if flag == 0:
        return JSONResponse(status_code=404,content={"message" : f"Item Name {item_name} does not exist."})

    return itemNameList

@app.get("/get/particular/itemBrand/{itembrand}")
def get_particular_itemName(itembrand : str):
    existing_data = load_data_from_getadminjson()
    flag = 0
    itemNameList = []
    for i,record in enumerate(existing_data):
        if(record["itemBrand"] == itembrand):
            flag = 1
            itemNameList.append(record)
    if flag == 0:
        return JSONResponse(status_code=404,content={"message" : f"Item Brand {itembrand} does not exist."})

    return itemNameList

@app.get("/get/data/particularDate/DateString")
def getParticularDataOnDate(date : str):
    existing_data = load_data_from_getadminjson()
    flag = 0
    output_list = []
    for record in existing_data:
        if(record["date"] == date):
            flag = 1
            output_list.append(record)
    if flag == 0:
        return JSONResponse(status_code=404,content={"message" : f"There is no data for {date}"})    
    return output_list


@app.delete("/delete/data/boughtdata")
def delele_particular_bought_data(admindata : AdminData):
    existing_data = load_data_from_getadminjson()

    for i,value in enumerate(existing_data):
        if(value["itemName"] == admindata.itemName and value["totalQuantity"] == admindata.totalQuantity and value["date"] == admindata.date and value["itemBrand"] == admindata.itemBrand and value["boughtPersonName"] == admindata.boughtPersonName):
            existing_data.pop(i)
            save_data_to_getadminjson(existing_data)
            return JSONResponse(status_code=200,content={"message" : "Record Deleted SuccessFully."})

    return JSONResponse(status_code=404,content="Record Not Found!")

@app.put("/update/data/boughtdata")
def update_particular_bought_data(itemname : str , totalquantity : int , date : str , itembrand : str , cost : float , boughtperson : str , adminData : AdminData):
    existing_data = load_data_from_getadminjson()
    new_data = adminData.model_dump()

    for i,record in enumerate(existing_data):
        if(record["itemName"] == itemname and record["totalQuantity"] == totalquantity and record["date"] == date and record["itemBrand"] == itembrand and record["cost"] == cost and record["boughtPersonName"] == boughtperson):
            existing_data[i] = new_data
            save_data_to_getadminjson(existing_data)
            return JSONResponse(status_code=200,content={"message" : "Data Updated Successfully!"})
    return JSONResponse(status_code=404,content="Data Not Found!")          
    

