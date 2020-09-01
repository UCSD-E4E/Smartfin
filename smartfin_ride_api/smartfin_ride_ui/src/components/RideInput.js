import React, { useState, useContext } from 'react'
import { RideContext } from '../contexts/RideContext'
import WithFetchRide from './WithFetchRide'

function RideInput({ fetchRide }) {
   
    const [rideId, setRideId] = useState('')
    const { dispatch } = useContext(RideContext)

    function handleChange(e) {
        setRideId(e.target.value)
    }

    // function fetchRide(e) {
    //     e.preventDefault()

    //     if (rideId.length < 5) {
    //         console.log('please enter a valid ride id')
    //         return
    //     }

    //     let url = `http://127.0.0.1:8000/ride/ride-create/${rideId}/`

    //     // fetch data of ride inputted
    //     fetch(url)
    //         .then(response => response.json())
    //         .then(data => {
    //              // set ride data
    //             dispatch({
    //                 type: 'SET_RIDE_DATA',
    //                 payload: {
    //                     rideId: data['rideId'],
    //                     loc1: data['loc1'],
    //                     loc3: data['loc3'],
    //                     startTime: data['startTime'],
    //                     endTime: data['endTime'],
    //                     heightSmartfin: data['heightSmartfin'],
    //                     heightList: JSON.parse(data['heightList']),
    //                     heightSampleRate: data['heightSampleRate'],
    //                     tempSmartfin: data['tempSmartfin'],
    //                     tempList: JSON.parse(data['tempList']),
    //                     tempSampleRate: data['tempSampleRate'],
    //                     buoyCDIP: data['buoyCDIP'],
    //                     heightCDIP: data['heightCDIP'],
    //                     tempCDIP: data['tempCDIP'],
    //                     latitude: data['latitude'],
    //                     longitude: data['longitude'],
    //                 }
    //             })
    //         })
    //         .catch(function(error){
    //             console.log('ERROR:', error)
    //         })

    //     setRideId('')
    // } 

    
    return (
        <div className="search-wrapper">
            <form onSubmit={e => {
                fetchRide(e, rideId)
                setRideId('')
            }}>
                <input type="text" onChange={e => handleChange(e)} value={rideId} />
                <input type="submit" value="Fetch Ride" />
            </form>
        </div>
    )
}

export default WithFetchRide(RideInput)
