import React, { useState } from 'react'
import IMUGraph from './IMUGraph'

export default function InteractiveGraph() {

    const [rideId, setRideId] = useState()
    const [startTime, setStartTime] = useState()
    const [endTime, setEndTime] = useState()
    const [timeRange, setTimeRange] = useState([])

    const handleRideSubmit = e => {
        e.preventDefault()
        console.log(rideId)
        // setRideId(id)
    }

    const handleRangeSubmit = e => {
        e.preventDefault()
        console.log(startTime)
        console.log(endTime)
        // setTimeRange([start, end])
        // setRange
    }


    return (
        <div className="graph-container">
            <div className="inputs">
                <form className="id-input" onSubmit={e => handleRideSubmit(e)}>
                    <label>
                        Ride Id: 
                        <input type="text" pattern="[0-9]*" onChange={e => setRideId(e.target.value)} />
                    </label>
                    <input type="submit" value="load new ride"/>
                </form>
                <form className="timerange-input" onSubmit={e => handleRangeSubmit(e)}>
                    <input type="text" pattern="[0-9]*" onChange={e => setStartTime(e.target.value)} />
                    <input type="text" pattern="[0-9]*" onChange={e => setEndTime(e.target.value)} />
                    <input type="submit" value="view new timerange" />
                </form>
            </div>
            <IMUGraph className="graph" rideId={rideId} timeRange={timeRange} />
        </div>
    )
}
