import React, { useState, useEffect, useRef } from 'react'

import CanvasJSReact from '../../assets/canvasjs.react';
import WithFetchAll from '../WithFetchAll';
import useFetchAll from '../../hooks/useFetchAll';
var CanvasJSChart = CanvasJSReact.CanvasJSChart;

function CompGraph({ showRidePopup, activeTab, loc1, loc3 }) {
    
    const [chartData, setChartData] = useState({})
    const [onLocation, setOnLocation] = useFetchAll(loc1, loc3, activeTab, chart)

    // independent of rideData
    const chartWrapper = useRef(0)

    // TODO: figure out how to update all rides graphs when a new ride is added

    function showHeightComparisonGraph(dataObj) {
        let  {rideId, heightSmartfin, heightCDIP, startTime} = dataObj
        let dataSmartfin = buildCompareChartData(rideId, heightSmartfin, startTime)
        let dataCDIP = buildCompareChartData(rideId, heightCDIP, startTime)
        return {
            labels: {
                extras: (<button onClick={() => setOnLocation(!onLocation)}>loc</button>),
                title: 'CDIP/Smartfin Height Comparison', 
                x: 'time (UNIX Timestamp)',
                y: 'wave height (m)',
            },
            data: [{
                click: e => showRidePopup({
                    rideId: e.dataPoint.id, 
                    rideDate: e.dataPoint.x.toString()}),
                type: 'line',
                name: 'Smartfin',
                showInLegend: true,
                dataPoints: dataSmartfin, 
            },
            {
                click: e => showRidePopup({
                    rideId: e.dataPoint.id, 
                    rideDate: e.dataPoint.x.toString()}),
                type: 'line',
                name: 'CDIP',
                showInLegend: true,
                dataPoints: dataCDIP, 
            }],
        }
    }

    function showTempComparisonGraph(dataObj) {
        let {rideId, tempSmartfin, tempCDIP, startTime} = dataObj
        let dataSmartfin = buildCompareChartData(rideId, tempSmartfin, startTime)
        let dataCDIP = buildCompareChartData(rideId, tempCDIP, startTime)
        return {
            chartType: 'c',
            labels: {
                extras: (<button onClick={() => setOnLocation(!onLocation)}>loc</button>),
                title: 'CDIP/Smartfin Surface Temp Comparison', 
                x: 'time (UNIX Timestamp)',
                y: 'ocean surface temp (C)',
            },
            data: [{
                click: e => showRidePopup({
                    rideId: e.dataPoint.id, 
                    rideDate: e.dataPoint.x.toString()}),
                type: 'line',
                name: 'Smartfin',
                showInLegend: true,
                dataPoints: dataSmartfin, 
            },
            {
                click: e => showRidePopup({
                    rideId: e.dataPoint.id, 
                    rideDate: e.dataPoint.x.toString()}),
                type: 'line',
                name: 'CDIP',
                showInLegend: true,
                dataPoints: dataCDIP, 
            }],
        }
    }

    function buildCompareChartData(rideId, data, times) {
        let timeRange = []
        timeRange = times.map(time => new Date(time)) 
        data = data.map((value, index) => ({x: timeRange[index], y: value, id: rideId[index]}))
        return data
    }


    function chart(response) {

        let graphData = {}  

        if(response['name'] === 'heights') 
            graphData = showHeightComparisonGraph(response['data'])
        else 
            graphData = showTempComparisonGraph(response['data'])

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

export default WithFetchAll(CompGraph)