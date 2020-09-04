import React, { useState, useEffect, useRef } from 'react'

import CanvasJSReact from '../../assets/canvasjs.react';
import WithFetchAll from '../WithFetchAll';
import useFetchAll from '../../hooks/useFetchAll';
var CanvasJSChart = CanvasJSReact.CanvasJSChart;

function RegressionGraph({ showRidePopup, activeTab, loc1, loc3 }) {
    
    const [chartData, setChartData] = useState({})
    const [onLocation, setOnLocation] = useFetchAll(loc1, loc3, activeTab, chart)

    // independent of rideData
    const chartWrapper = useRef(0)

    
    function showHeightRegressionGraph(dataObj) {
        let {rideId, heightSmartfin, heightCDIP} = dataObj
        let data = heightSmartfin.map((value, index) => ({x: value, y: heightCDIP[index], id: rideId[index]}))
        return {
            labels: {
                title: 'Smartfin/CDIP Height Regression', 
                extras: (<button onClick={() => setOnLocation(!onLocation)}>loc</button>),
                x: 'Heights calculated by Smartfin',
                y: 'Heights calculated by CDIP',
            },
            data: [{
                click: e => showRidePopup({
                    rideId: e['dataPoint']['id'], 
                    rideDate: e['dataPoint']['x']}),  
                type: 'scatter',
                toolTipContent: "Smartfin: {x}°C, CDIP: {y}°C",
                showInLegend: true,
                dataPoints: data, 
            }],
        }
    }

    function showTempRegressionGraph(dataObj) {
        let {rideId, tempSmartfin, tempCDIP} = dataObj
        let data = tempSmartfin.map((value, index) => ({x: value, y: tempCDIP[index], id: rideId[index]}))
        return {
            labels: {
                title: 'Smartfin/CDIP Temperature Regression',
                extras: (<button onClick={() => setOnLocation(!onLocation)}>loc</button>),
                x: 'Heights calculated by Smartfin',
                y: 'Heights calculated by CDIP',
            },
            data: [{
                click: e => showRidePopup({
                    rideId: e['dataPoint']['id'], 
                    rideDate: e['dataPoint']['x']}),  
                type: 'scatter',
                toolTipContent: "Smartfin: {x}°C, CDIP: {y}°C",
                showInLegend: true,
                dataPoints: data, 
            }],
        }
    }


    
  
    function chart(response) {

        let graphData = {}  

        if(response['name'] === 'heights') 
            graphData = showHeightRegressionGraph(response['data'])
        else 
            graphData = showTempRegressionGraph(response['data'])

        let {data, labels} = graphData
        let {extras, title, x, y} = labels
        let chartData = {
            header: title,
            extras: extras,
            theme: "light2", // "light1", "dark1", "dark2"
            animationEnabled: true,
            zoomEnabled: true,
            exportEnabled: true,
            toolTip: {
                shared: true
            },  
            width: chartWrapper.current.clientWidth,
            height: chartWrapper.current.clientHeight,         
            data: data,
            axisX: {
                title: x
            },
            axisY: {
                title: y,
            },			
        }

        // calculate time range of graph
        setChartData(chartData)
    }


    
    return (
        <div className="widget-wrapper">
            <div className="widget-heading">
                <div>{chartData['header']}</div>
                <div>{chartData['extras']}</div>
            </div>
            <div className="whitespace">whitespace</div>
            <div className="chart-wrapper" ref={chartWrapper}>
                <CanvasJSChart options={chartData}
                        // onRef={ref => this.chart = ref} 
                    />
            </div>
        </div>
    )
}

export default RegressionGraph