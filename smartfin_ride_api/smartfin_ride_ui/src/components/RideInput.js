import React, { useState, useContext } from 'react'
import { RideContext } from '../contexts/RideContext'

function RideInput() {
   
    const [rideId, setRideId] = useState('')
    const { rideData, dispatch } = useContext(RideContext)
    
    // function getCookie(name) {
    //     var cookieValue = null;
    //     if (document.cookie && document.cookie !== '') {
    //         var cookies = document.cookie.split(';');
    //         for (var i = 0; i < cookies.length; i++) {
    //             var cookie = cookies[i].trim();
    //             // Does this cookie string begin with the name we want?
    //             if (cookie.substring(0, name.length + 1) === (name + '=')) {
    //                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
    //                 break;
    //             }
    //         }
    //     }
    //     return cookieValue;
    // }

    

    function handleChange(e) {
        setRideId(e.target.value)
    }

    function handleSubmit(e) {
        e.preventDefault()

        if (rideId.length < 5) {
            console.log('please enter a valid ride id')
            return
        }

        let url = `http://127.0.0.1:8000/ride/ride-create/${rideId}/`

        // fetch data of ride inputted
        fetch(url)
        .then(response => response.json())
        .then(data => {
            processData(data)
        })
        .catch(function(error){
            console.log('ERROR:', error)
        })

        setRideId('')
    } 


    function processData(data) {

        // set ride data
        dispatch({
            type: 'SET_RIDE_DATA',
            payload: {
                rideId: data['rideId'],
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

        // process ocean and motion data
    }

    
    return (
        <div>
            <form onSubmit={e => handleSubmit(e)}>
                <input type="text" onChange={e => handleChange(e)} value={rideId} />
                <input type="submit" value="Fetch Data" />
            </form>
        </div>
    )
}

export default RideInput
