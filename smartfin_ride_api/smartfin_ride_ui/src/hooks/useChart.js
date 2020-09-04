import React from 'react'


// // TODO: figure this out
// function chart(response) {
//     console.log("in chart: ", response)
//     let graphData = {}  

//     if(response['name'] === 'heights') 
//         graphData = showHeightComparisonGraph(response['data'])
//     else 
//         graphData = showTempComparisonGraph(response['data'])

//     let {data, labels} = graphData
//     let {extras, title, x, y} = labels
//     let chartData = {
//         header: title,
//         extras: extras,
//         theme: "light2", // "light1", "dark1", "dark2"
//         animationEnabled: true,
//         zoomEnabled: true,
//         exportEnabled: true,
//         toolTip: {
//             shared: true
//         },  
//         width: chartWrapper.current.clientWidth,
//         height: chartWrapper.current.clientHeight,         
//         data: data,
//         axisX: {
//             title: x
//         },
//         axisY: {
//             title: y,
//         },			
//     }

//     // calculate time range of graph
//     return chartData
// }




// function useChart(response) {
//     useEffect()
//     return chartData
// }

// export default useChart