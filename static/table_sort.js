

function sortNumberAS(a, b) {
    return a - b
}

function sortNumberDesc(a, b) {
    return b-a
}

function SortTable(obj){
    var name=document.getElementsByName("td0");
    var date=document.getElementsByName("td1");
    var nameArray=[];
    var dateArray1=[];
    //存储现有数据到数组name和date
    for(var i=0;i<name.length;i++){
        nameArray.push(name[i].innerHTML);
    }
    for(var i=0;i<date.length;i++) {
        dateArray1.push(date[i].innerHTML);
    }
    //创建两个相同的待排序的数组old和new
    var oldArray=[];
    for(var i=0;i<date.length;i++){
        oldArray.push(Date.parse(date[i].innerHTML));
    }
    var newArray=[];
    for(var i=0;i<oldArray.length;i++){
        newArray.push(oldArray[i]);
    }
    //根据不同的排序方式对newArray数组进行排序
    if(obj.className=="text-center as"){
        newArray.sort(sortNumberAS);
        obj.className="text-center desc";
    }else{
        newArray.sort(sortNumberDesc);
        obj.className="text-center as";
    }
    //把old和new数组进行匹配，以name和date为数据源重新设置table中的内容
    for(var i=0;i<newArray.length;i++){
        for(var j=0;j<oldArray.length;j++){
            if(oldArray[j]==newArray[i]){
                document.getElementsByName("td0")[i].innerHTML=nameArray[j];
                document.getElementsByName("td1")[i].innerHTML=dateArray1[j];
                oldArray[j]=null;
                break;
            }
        }
    }
}

