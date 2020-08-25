import React, { useState, useEffect, useContext } from 'react'
import { RideContext } from '../contexts/RideContext'
import { Line } from 'react-chartjs-2'


function SmartGraph() {

    const {rideData, dispatch} = useContext(RideContext)
    const {tempList, tempSampleRate, heightList, heightSampleRate} = rideData

    const [heights, setHeights] = useState({})
    const [temps, setTemps] = useState({})

    const [chartData, setChartData] = useState({})

    const [currentData, setCurrentData] = useState([])
    const [currentTimeRange, setCurrentTimeRange] = useState(0)
    const [currentSamplerate, setCurrentSampleRate] = useState(0)
    const [currentDataTitle, setCurrentDataTitle] = useState('')

    // todo: graph stuff 

    function chart() {
        let timeRange = [...Array(currentData.length).keys()]
        timeRange = timeRange.map(i => i * currentSamplerate)
        setChartData({
            labels: timeRange,
            datasets: [{
                label: currentDataTitle,
                data: currentData,
                backgroundColor: [
                    'rgb(75, 192, 192, 1)'
                ],
                color: [
                    'rbga(123, 45, 48, 1)'
                ],
                fill: false,
                borderWidth: 4
            }]
        })
    }

    useEffect(() => {
        getAllRides()
    }, [rideData])

    useEffect(() => {
        showRideTempGraph()
    }, [])

    useEffect(() => {
        chart()
    }, [currentData])

  
    function getAllRides() {
        let urlHeights = "http://127.0.0.1:8000/ride/height-list/"
        let urlTemps = "http://127.0.0.1:8000/ride/temp-list/"

        fetch(urlHeights)
        .then(response => response.json())
        .then(data => {
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

        showRideTempGraph()
    }

    function showRideTempGraph() {
        setCurrentData(tempList)
        setCurrentTimeRange(tempList.length)
        setCurrentSampleRate(tempSampleRate)
        setCurrentDataTitle('Temperature')
    }

    function showRideHeightGraph() {
        setCurrentData(heightList)
        setCurrentTimeRange(heightList.length)
        setCurrentSampleRate(heightSampleRate)
        setCurrentDataTitle('Height')
    }

    // wait for when the user has the mouse down
    // when user mouse down:
    //      store the x value the user presses the mouse down
    //      draw lines to show how far user has dragge
    //      calculate x length of rectangle being drawn
    // when user mouse up 
    //      calculate the start time
    //          get how far along x axis the start point was
    //          multiply that fraction with the total duration being plotted
    //      calculate the end time
    //          get how far along x axis the end point was
    //          multiply that fraction with the total duration being plotted
    //      redraw the grid, only plotting the data point between the start and end points
  
    // vars to store: 
    //      start: x location on graph of mouse down
    //      end: x location on graph of mouse up
    //      time: the array of time being plotted (default is taken from what the ride duration already is from RideContext)
    //      data: the data being plotted at a 1:1 ratio with the time

    // how to test:
    //      make fake values to plot

    // how to implement:
    //      render graph in a canvas element?
    return (
        <div>
            smartgraph
            {JSON.stringify(heights)}
            {JSON.stringify(temps)}
            <div>
                smartfin ride heights
                <button onClick={showRideHeightGraph}>heights</button>
                <button onClick={showRideTempGraph}>temps</button>
                <Line data={chartData} options={{
                    title: currentDataTitle,
                    

                }} />
            </div>
        </div>
    )
}

export default SmartGraph