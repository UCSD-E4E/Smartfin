
import React, { useContext, useState, useEffect } from 'react'
import { RideContext } from './contexts/RideContext'
import RideInput from './components/RideInput'
import SmartGraph from './components/SmartGraph' 


function SmartfinUI() {

    const { rideData } = useContext(RideContext)
    const { rideId, loc1, loc3, latitude, longitude, startTime, endTime } = rideData

    const [duration, setDuration] = useState('')
    const [rideTime, setRideTime] = useState('')
    const [rideLocation, setRideLocation] = useState({
        city: '',
        state: ''
    })
    
// TODO: fix duration by only calculating the actual time different and remove the date since Date() doesnt part days over 28 i think

    // calculate ride duration
    useEffect(() => {
        setRideTime(convertToTime(startTime))
        setDuration(calculateRideDuration(startTime, endTime))
    }, [startTime, endTime])

    // useEffect(() => {
    //     findCity(latitude, longitude)
    // }, [rideData])

    // function findCity(latitude, longitude) {
    //     let key = "AIzaSyCV3zZ2YhNOsf9DN8CvSiH1NBJC3XdMYs4"
    //     let url = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&sensor=true&key=${key}`
    //     console.log(url)
    //     fetch(url)
    //         .then(response => response.json())
    //         .then(data => {
    //             try {
    //                 console.log(data['results'][0]['address_components'])
    //                 setRideLocation({
    //                     city: data['results'][0]['address_components'][2]['long_name'], 
    //                     state: data['results'][0]['address_components'][4]['short_name']
    //                 })
    //             } catch {
    //                 console.log('no')
    //             }
                    
    //         })
    // }

    // calculate
    function calculateRideDuration(startTime, endTime) {
        let [shr, smin, ssec] = startTime.substring(11, 19).split(':')
        let [ehr, emin, esec] = endTime.substring(11, 19).split(':')

        shr = parseInt(shr) * 60
        ehr = parseInt(ehr) * 60

        smin = parseInt(smin)
        emin = parseInt(emin)

        ssec = parseInt(ssec) / 60
        esec = parseInt(esec) / 60

        let startTimeI = shr + smin + ssec
        let endTimeI = ehr + emin + esec
        let duration = endTimeI - startTimeI
        duration = duration.toFixed(1)

        return duration
    }


    function convertToTime(time) {
        time = (new Date(time)).toString()
        let hourStr = time.substring(16,18)
        let hourInt = parseInt(hourStr)
        let half = 'am'
        if(hourInt > 12) {
             hourInt -= 12
            half = 'pm'
        }
        hourStr = hourInt.toString()
        // hourStr = ("0" + hourStr).slice(-2);
        return time.substring(0,16) + hourStr + time.substring(18,22) + half + ' (PST)'
    }

   
    return (
        <div className="smartfin-ui">
            <div className="app-wrapper">
                <div className="app-title-wrapper">
                    <h1>Smartfin Ride API</h1>
                </div>
                {rideData['rideId'] === '' ?
                
                    <div className="ride-input-wrapper">
                        <RideInput className="ride-input"/>
                    </div> 
                    
                    :

                    <div className="ui-wrapper wrapper">
                        <div className="header-wrapper wrapper layout">
                            
                            <div className="title-wrapper">
                                <label className="ride-id-wrapper title-txt thin-txt">Ride #{rideId}</label>
                                <h2 className="location-wrapper title-txt">{loc1}, {loc3}</h2>
                            </div>
                            <div className="input-wrapper">
                                <RideInput className="ride-input"/>
                            </div>
                        </div>
                        <SmartGraph />
                        <div className="footer-wrapper wrapper layout">
                            <div className="location-wrapper">
                                <p>coordinates: ({latitude}, {longitude})</p>
                            </div>
                            <div className="ride-date-wrapper">
                                <p>ride date: {rideTime}</p>
                            </div>
                            <div className="ride-duration-wrapper">
                                <p>ride duration: {duration} mins</p>
                            </div>
                        </div>
                    </div>  
                }     
            </div>
        </div>
    )
}


export default SmartfinUI