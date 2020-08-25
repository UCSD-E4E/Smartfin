
import React, { useContext, useState, useEffect } from 'react'
import RideContextProvider, { RideContext } from './contexts/RideContext'
import RideInput from './components/RideInput'
import SmartGraph from './components/SmartGraph'

function SmartfinUI() {

    const { dispatch, rideData } = useContext(RideContext)
    const { latitude, longitude, startTime, endTime } = rideData

    const [duration, setDuration] = useState('')
    const [date, setDate] = useState('')
    const [time, setTime] = useState('')
    
// TODO: fix duration by only calculating the actual time different and remove the date since Date() doesnt part days over 28 i think

    // calculate ride duration
    useEffect(() => {
        setDate(convertToDate(startTime))
        setTime(convertToTime(startTime))
        setDuration(calculateRideDuration(startTime, endTime))
    }, [startTime])


    // calculate
    function calculateRideDuration(startTime, endTime) {

        let [shr, smin, ssec] = startTime.substring(10, 19).split(':')
        let [ehr, emin, esec] = endTime.substring(10, 19).split(':')

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
        let hourStr = time.substring(11,13)
        let hourInt = parseInt(hourStr)
        let half = 'am'
        if(hourInt > 12) {
            hourInt -= 12
            half = 'pm'
        }
        hourStr = hourInt.toString()
        return hourStr + time.substring(13, 16) + half
    }


    function convertToDate(time) {
        let day = time.substring(0,2)
        let month = time.substring(3,5)
        let year = time.substring(6,10)

        switch(month) {
            case '01': month = 'January'
                break
            case '02': month = 'February'
                break
            case '03': month = 'March'
                break
            case '04': month = 'April'
                break
            case '05': month = 'May'
                break
            case '06': month = 'June'
                break
            case '07': month = 'July'
                break
            case '08': month = 'August'
                break
            case '09': month = 'September'
                break
            case '10': month = 'October'
                break
            case '11': month = 'November'
                break
            case '12': month = 'December'
                break
            default: month = 'nan'
        }

        return month +' '+ day +'/'+ year
    }
   
    return (
        <div>
            {rideData['rideId'] === '' ?
            
                <div className="ride-input-wrapper">
                    <RideInput className="ride-input"/>
                </div> 
                
                :

                <div className="ui-wrapper wrapper">
                    <div className="header-wrapper wrapper layout">
                        header
                        <RideInput className="ride-input"/>
                    </div>
                    <div className="body=wrapper wrapper layout">
                        body
                        <SmartGraph />
                        {JSON.stringify(rideData)}
                    </div>
                    <div className="footer-wrapper wrapper layout">
                        <p>latitude: {latitude}</p>
                        <p>longitude: {longitude}</p>
                        <p>ride date: {date+' @ '+time}</p>
                        <p>ride duration: {duration} mins</p>
                    </div>
                </div>  
                
            }      
        </div>
    )
}


export default SmartfinUI