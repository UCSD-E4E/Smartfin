import React, { useState, useEffect, useContext, useRef } from 'react'
import { RideContext } from '../contexts/RideContext'

import { Tabs, Tab } from '@material-ui/core';

import CanvasJSReact from '../assets/canvasjs.react';
var CanvasJSChart = CanvasJSReact.CanvasJSChart;


// [14796, 13359, 13118, 12988, 12985, 12984, 12983, 12982, 12981, 12980, 12979, 12884, 12863, 12862, 12843, 12833, 12747, 12721, 12705, 12704, 12703, 12702, 12701, 12700, 12699, 12696, 12694, 12693, 12692, 12673, 12533, 12531, 12530, 12502, 12488, 12484, 12477, 12476, 12250, 12187, 12186, 12181, 12180, 12179, 12178, 12177, 12147, 12146, 12140, 12093, 12088, 12086, 12084, 12081, 12027, 12026, 12025, 12024, 12022, 12021, 12020, 12019, 12018, 12008, 11982, 11974, 11947, 11943, 11912, 11907, 11906, 11897, 11896, 11895, 11822, 11821, 11769, 11764, 11763, 11762, 11761, 11760, 11759, 11751, 11750, 11730, 11713, 11709, 11695, 11670, 11663, 11636, 11603, 11552, 11543, 11542, 11538, 11534, 11533, 11528, 11521, 11518, 11516, 11506, 11505, 11502, 11475, 11460, 11442, 11420, 11419, 11416, 11415, 11409, 11398, 11390, 11378, 11219, 11209, 11207, 11176, 11173, 11168, 11167, 11165, 11163, 11161, 11158, 11157, 11151, 11126, 11119, 11051, 11049, 11047, 11045, 11044, 11015, 11009, 11008, 10967, 10922, 10921, 10893, 10887, 10884, 10880, 10875, 10866, 10865, 10822, 10804, 10784]

//TODO: figure out how to update the models in the database whenever we change integration methods
// have the different graph views show different information in the graph info area
// make the graphs all widgets
// widget component: props: graphdata, chart (maybe make a template based componenet like in django)
// pretty much make this class a widget, so each widget can work and make queries on its own
function SmartGraph() {

    // ride context data
    const {dispatch, rideData} = useContext(RideContext)
    const {rideId, loc1, loc3, tempList, tempSampleRate, heightList, heightSampleRate} = rideData

    // independent of rideData
    const [heights, setHeights] = useState(null)
    const [temps, setTemps] = useState(null)

    // info of ride in comparison and regression graphs
    const [rideInfo, setRideInfo] = useState('')

    // whether to retrieve all rides or just ones on location
    const [onLocation, setOnLocation] = useState(false)

    // chart data
    const chartWrapper = useRef(0)
    const [chartData, setChartData] = useState([])
    const [activeTab, setActiveTab] = useState(0)
    

    useEffect(() => {
        getAllRides()
    }, [onLocation])

    useEffect(() => {
        setOnLocation(false)
        getAllRides()
        setActiveTab(0)
    }, [rideData])

    useEffect(() => {
        if(heights != null && temps != null) {
            chart()
        }
    }, [heights, temps, activeTab])



    // GRAPH VIEW FUNCTIONS -------------------------------------------    
// TODO: format ride duration to one decimal point in graph lebelling

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

    function showHeightComparisonGraph() {
        let  {rideId, heightSmartfin, heightCDIP, startTime} = heights
        console.log('heights: ', heights)
        let dataSmartfin = buildCompareChartData(rideId, heightSmartfin, startTime)
        let dataCDIP = buildCompareChartData(rideId, heightCDIP, startTime)
        return {
            labels: {
                title: 'CDIP/Smartfin Height Comparison', 
                x: 'time (UNIX Timestamp)',
                y: 'wave height (m)',
            },
            data: [{
                click: e => handleClick(e),
                type: 'line',
                name: 'Smartfin',
                showInLegend: true,
                dataPoints: dataSmartfin, 
            },
            {
                click: e => handleClick(e),
                type: 'line',
                name: 'CDIP',
                showInLegend: true,
                dataPoints: dataCDIP, 
            }],
        }
    }

    function showTempComparisonGraph() {
        let {rideId, tempSmartfin, tempCDIP, startTime} = temps
        let dataSmartfin = buildCompareChartData(rideId, tempSmartfin, startTime)
        let dataCDIP = buildCompareChartData(rideId, tempCDIP, startTime)
        return {
            chartType: 'c',
            labels: {
                title: 'CDIP/Smartfin Surface Temp Comparison', 
                x: 'time (UNIX Timestamp)',
                y: 'ocean surface temp (C)',
            },
            data: [{
                click: e => handleClick(e),
                type: 'line',
                name: 'Smartfin',
                showInLegend: true,
                dataPoints: dataSmartfin, 
            },
            {
                click: e => handleClick(e),
                type: 'line',
                name: 'CDIP',
                showInLegend: true,
                dataPoints: dataCDIP, 
            }],
        }
    }

    function showHeightRegressionGraph() {
        let {rideId, heightSmartfin, heightCDIP} = heights
         let data = heightSmartfin.map((value, index) => ({x: value, y: heightCDIP[index], id: rideId[index]}))
        return {
            labels: {
                title: 'Smartfin/CDIP Height Regression', 
                x: 'Heights calculated by Smartfin',
                y: 'Heights calculated by CDIP',
            },
            data: [{
                click: e => handleClick(e),
                type: 'scatter',
                toolTipContent: "Smartfin: {x}°C, CDIP: {y}°C",
                showInLegend: true,
                dataPoints: data, 
            }],
        }
    }

    function showTempRegressionGraph() {
        let {rideId, tempSmartfin, tempCDIP} = temps
        let data = tempSmartfin.map((value, index) => ({x: value, y: tempCDIP[index], id: rideId[index]}))
        return {
            labels: {
                title: 'Smartfin/CDIP Temperature Regression',
                extras: (<button onClick={() => setOnLocation(!onLocation)}>
                            {onLocation ? "Filter rides in this location" : "View all rides"}
                            </button>),
                x: 'Heights calculated by Smartfin',
                y: 'Heights calculated by CDIP',
            },
            data: [{
                click: e => handleClick(e),
                type: 'scatter',
                toolTipContent: "Smartfin: {x}°C, CDIP: {y}°C",
                showInLegend: true,
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

    function buildCompareChartData(rideId, data, times) {
        let timeRange = []
        timeRange = times.map(time => new Date(time)) 
        data = data.map((value, index) => ({x: timeRange[index], y: value, id: rideId[index]}))
        return data
    }
   

    function chart() {

        let data = {}
        if(activeTab === 1) 
            data = [
                showRideTempGraph(),
                showTempComparisonGraph(),
                showTempRegressionGraph(),
            ]
        else 
            data = [
                showRideHeightGraph(),
                showHeightComparisonGraph(),
                showHeightRegressionGraph(),
            ]
        
        let d = []
        data.map((graphData, index) => {
            let {data, labels} = graphData
            let {extras, title, x, y} = labels
            d.push({
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
            })
        })

        // calculate time range of graph
        setChartData(d)
    }



    // DATA FETCHING FUNCTIONS -------------------------------------------
    function viewNewRide() {
        let url = `http://127.0.0.1:8000/ride/ride-create/${rideInfo}/`

        // fetch data of ride inputted
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // set ride data
                dispatch({
                    type: 'SET_RIDE_DATA',
                    payload: {
                        rideId: data['rideId'],
                        loc1: data['loc1'],
                        loc3: data['loc3'],
                        startTime: data['startTime'],
                        endTime: data['endTime'],
                        heightSmartfin: data['heightSmartfin'],
                        heightList: JSON.parse(data['heightList']),
                        heightSampleRate: data['heightSampleRate'],
                        tempSmartfin: data['tempSmartfin'],
                        tempList: JSON.parse(data['tempList']),
                        tempSampleRate: data['tempSampleRate'],
                        buoyCDIP: data['buoyCDIP'],
                        heightCDIP: data['heightCDIP'],
                        tempCDIP: data['tempCDIP'],
                        latitude: data['latitude'],
                        longitude: data['longitude'],
                    }
                })
            })
            .catch(function(error){
                console.log('ERROR:', error)
            })
        setActiveTab(0)
    }

    // fetch height and temperature info from all rides in db
    function getAllRides() {
        let location = 'all'
        if (onLocation) location = loc1 + ':' + loc3

        let urlHeights = `http://127.0.0.1:8000/ride/height-list/${location}`
        let urlTemps = `http://127.0.0.1:8000/ride/temp-list/${location}`

        fetch(urlHeights)
            .then(response => response.json())
            .then(data => {
                console.log('from getallrides: ', data)
                setHeights(data)
            })
            .catch(function(error){
                console.log('ERROR:', error)
            })

        fetch(urlTemps)
            .then(response => response.json())
            .then(data => {
                setTemps(data)
            })
            .catch(function(error){
                console.log('ERROR:', error)
            })
    }
    


    function handleClick(e) {
        setRideInfo(e['dataPoint']['id'])
    }

    const handleChange = (event, newValue) => {
        setActiveTab(newValue)
    }

    
// TODO: split up the chart data into having 3 keys, have the only toggle be the temperature difference
//          put the temperature/height tabs into the tab that already existing
    return (
        <div className="body-wrapper">
           
            <div className="body-header-wrapper layout">
                <Tabs
                    value={activeTab}
                    textColor="inherit"
                    onChange={handleChange}
                    aria-label="graph-selector"
                    orientation="vertical"
                >
                    <Tab label="Heights" />
                    <Tab label="Temps" />
                </Tabs>
            </div>
            <div className="widget-body-wrapper layout">
                <div className="widget-area-wrapper">
                    {chartData.map((data, index) => (
                        <div className="widget-wrapper" key={index}>
                            <div className="chart-heading">
                                <div>{data['header']}</div>
                                <div>{data['extras']}</div>
                            </div>
                            <div className="chart-wrapper" ref={chartWrapper}>
                                <CanvasJSChart options={data} key={index}
                                        // onRef={ref => this.chart = ref} 
                                    />
                            </div>
                        </div>
                    ))}
                </div>
                {/* <div className="chart-info-wrapper layout">
                    <button onClick={viewNewRide} className="info-btn">View Ride #{rideInfo}</button>
                    <button onClick={() => setOnLocation(!onLocation)} className="info-btn">
                        {onLocation ? "view all rides" : "view only rides in this location"}
                        </button>
                </div>        */}
            </div>    
        </div>
    )
}

export default SmartGraph