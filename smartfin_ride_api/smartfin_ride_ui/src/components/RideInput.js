import React, { useState, useContext } from 'react'
import { RideContext } from '../contexts/RideContext'
import WithFetchRide from './WithFetchRide'
import useFetchRide from '../hooks/useFetchRide'

function RideInput() {
   
    const [rideId, setRideId] = useState('')
    const { dispatch } = useContext(RideContext)
    const fetchRide = useFetchRide()

    function handleChange(e) {
        setRideId(e.target.value)
    }

    
    return (
        <div className="search-wrapper">
            <form onSubmit={e => {
                e.preventDefault()
                fetchRide(rideId, dispatch)
                setRideId('')
            }}>
                <input type="text" onChange={e => handleChange(e)} value={rideId} />
                <input type="submit" value="Fetch Ride" />
            </form>
        </div>
    )
}

export default RideInput
