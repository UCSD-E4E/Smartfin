import React, { useContext } from 'react'
import { RideContext } from '../../contexts/RideContext'
import WithFetchRide from '../WithFetchRide'

function RidePopUp({ data, setShowPopup, fetchRide }) {

    const { dispatch } = useContext(RideContext)
    const { rideId, rideDate } = data

    // TODO: figure out how to dispatch inside of the HOC or more HOC functions to custom hooks
    
    return (
        <div onClick={() => setShowPopup(false)} className="pop-up-wrapper">
            <div className="widget-heading">
                <div>Ride Info</div>
            </div>
            <div className="widget-body">
                <div>Ride #{rideId}</div>
                <div>Date: {rideDate}</div>
                <button onClick={e => fetchRide(e, rideId)}>View Ride</button>
            </div>
            
        </div>
    )
}

export default WithFetchRide(RidePopUp)