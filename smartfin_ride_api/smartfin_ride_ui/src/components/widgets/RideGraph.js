import React, { useState, useContext, useEffect, useRef } from 'react'

import CanvasJSReact from '../../assets/canvasjs.react';
import { RideContext } from '../../contexts/RideContext';
var CanvasJSChart = CanvasJSReact.CanvasJSChart;


function RideGraph({ activeTab }) {

    const {rideData} = useContext(RideContext)
    const {tempList, tempSampleRate, heightList, heightSampleRate} = rideData

    const [chartData, setChartData] = useState({})
    const chartWrapper = useRef(0)

    useEffect(() => {
        chart()
    }, [rideData, activeTab])

    function showRideHeightGraph() {
        let data = buildRideChartData(heightList, heightList.length, heightSampleRate)
        return {
            labels: {
                title: 'Wave Heights', 
                x: 'time (min)',
                y: 'wave height (m)',
            },
            data: [{
                type: 'line',
                toolTipContent: "Ride duration {x}min: Temperature: {y}C",
                dataPoints: data, 
            }],
        }
    }

    function showRideTempGraph() {

        let data = buildRideChartData(tempList, tempList.length, tempSampleRate)
        return {
            labels: {
                title: 'Ocean Surface Temperature', 
                x: 'time (min)',
                y: 'temperature (C)',
            },
            data: [{
                type: 'line',
                toolTipContent: "Ride duration {x}min: Displacement: {y}m",
                dataPoints: data,
            }], 
        }
    }

    function buildRideChartData(data, range, rate) {
        let timeRange = []
        timeRange = [...Array(range).keys()]
        timeRange = timeRange.map(i => (i * rate) / 60)
        data = data.map((value, index) => ({x: timeRange[index], y: value}))
        return data
    }

    function chart() {

        console.log(activeTab)
        let graphData = {}  

        if(activeTab === 1) 
            graphData = showRideTempGraph()
        else 
            graphData = showRideHeightGraph()

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


export default RideGraph