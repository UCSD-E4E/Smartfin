import React, { useState, useEffect, useContext } from 'react'
import { RideContext } from '../contexts/RideContext'

import RideGraph from './widgets/RideGraph';
import CompGraph from './widgets/CompGraph';
import RegressionGraph from './widgets/RegressionGraph';
import RidePopUp from './widgets/RidePopUp';


// [14796, 13359, 13118, 12988, 12985, 12984, 12983, 12982, 12981, 12980, 12979, 12884, 12863, 12862, 12843, 12833, 12747, 12721, 12705, 12704, 12703, 12702, 12701, 12700, 12699, 12696, 12694, 12693, 12692, 12673, 12533, 12531, 12530, 12502, 12488, 12484, 12477, 12476, 12250, 12187, 12186, 12181, 12180, 12179, 12178, 12177, 12147, 12146, 12140, 12093, 12088, 12086, 12084, 12081, 12027, 12026, 12025, 12024, 12022, 12021, 12020, 12019, 12018, 12008, 11982, 11974, 11947, 11943, 11912, 11907, 11906, 11897, 11896, 11895, 11822, 11821, 11769, 11764, 11763, 11762, 11761, 11760, 11759, 11751, 11750, 11730, 11713, 11709, 11695, 11670, 11663, 11636, 11603, 11552, 11543, 11542, 11538, 11534, 11533, 11528, 11521, 11518, 11516, 11506, 11505, 11502, 11475, 11460, 11442, 11420, 11419, 11416, 11415, 11409, 11398, 11390, 11378, 11219, 11209, 11207, 11176, 11173, 11168, 11167, 11165, 11163, 11161, 11158, 11157, 11151, 11126, 11119, 11051, 11049, 11047, 11045, 11044, 11015, 11009, 11008, 10967, 10922, 10921, 10893, 10887, 10884, 10880, 10875, 10866, 10865, 10822, 10804, 10784]

//TODO: figure out how to update the models in the database whenever we change integration methods
function WidgetArea({ activeTab, setActiveTab }) {

    // ride context data
    const {rideData, dispatch} = useContext(RideContext)
    const {loc1, loc3} = rideData
    const [showPopup, setShowPopup] = useState(false)
    const [popupData, setPopupData] = useState({rideId: '', rideDate: ''})

    useEffect(() => {
        setActiveTab(0)
    }, [rideData])

    function showRidePopup(data) {
        console.log(data)
        setShowPopup(true)
        setPopupData({...data})
    }
   
    
// TODO: split up the chart data into having 3 keys, have the only toggle be the temperature difference
//          put the temperature/height tabs into the tab that already existing
    return (
        <div className="body-wrapper">
            <div className="widget-body-wrapper layout">
                {showPopup ? <RidePopUp dispatch={dispatch} data={popupData} setShowPopup={setShowPopup} /> : ""}
                <div className="widget-area-wrapper">
                    <RideGraph activeTab={activeTab} />
                    <CompGraph 
                        activeTab={activeTab} 
                        loc1={loc1} 
                        loc3={loc3}
                        showRidePopup={showRidePopup} />
                    <RegressionGraph 
                        activeTab={activeTab} 
                        loc1={loc1} 
                        loc3={loc3}
                        showRidePop={showRidePopup} />
                </div>
            </div>    
        </div>
    )
}

export default WidgetArea