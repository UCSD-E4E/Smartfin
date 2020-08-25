import React, { createContext, useReducer } from "react";
import RideReducer from "../reducers/RideReducer";


const RideData = {
    rideId: '',
    startTime: '',
    endTime: '',
    heightSmartfin: 0.0,
    heightList: '',
    heightSampleRate: 0,
    tempSmartfin: 0.0,
    tempList: '',
    tempSampleRate: 0,
    buoyCDIP: '',
    heightCDIP: 0.0,
    tempCDIP: 0.0,
    latitude: 0.0,
    longitude: 0.0,
}


export const RideContext = createContext()

function RideContextProvider(props) {

    const [rideData, dispatch] = useReducer(RideReducer, RideData)

    return (
        <RideContext.Provider value={{ rideData, dispatch }} >
            {props.children}
        </RideContext.Provider>
    )
}

export default RideContextProvider