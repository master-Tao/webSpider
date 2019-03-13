
var arr=document.getElementById('count').getAttribute('data').split(",");
arr.pop();
var item_name = arr[0];
var date=[];
var num=[];

for(var i=0;i<(arr.length-1)/2;i++){
    date.push(arr[i*2+1]);
    num.push(parseInt(arr[i*2+2]));
}

$(function () {
    $('#container').highcharts({
        chart: {
            type: 'line'
        },
        title: {
            text: '  '
        },
        xAxis: {
            categories: date
        },
        yAxis: {
            title: {
                text: '评论量'
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true          // 开启数据标签
                },
                enableMouseTracking: false // 关闭鼠标跟踪，对应的提示框、点击事件会失效
            }
        },
        series: [{
            name: item_name,
            data: num
        }]
    })
});