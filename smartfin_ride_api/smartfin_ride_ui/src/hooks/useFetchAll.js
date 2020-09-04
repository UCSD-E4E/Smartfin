import { useState, useEffect } from 'react'

function fetchAll(onLocation, loc1, loc3, activeTab, chart) {
    let location = 'all'
    if (onLocation) location = loc1 + ':' + loc3
    
    if(activeTab === 0) {
        let urlHeights = `http://127.0.0.1:8000/ride/height-list/${location}`
        fetch(urlHeights)
        .then(response => response.json())
        .then(heights => {
            chart({name: 'heights', data: heights})
        })
        .catch(function(error){
            console.log('ERROR:', error)
        })
    } else {
        let urlTemps = `http://127.0.0.1:8000/ride/temp-list/${location}`
        fetch(urlTemps)
        .then(response => response.json())
        .then(temps => {
            chart({name: 'temps', data: temps})
        })
        .catch(function(error){
            console.log('ERROR:', error)
        })
    }
}


function useFetchAll(loc1, loc3, activeTab, chart) {

    const [onLocation, setOnLocation] = useState(false)
   
    useEffect(() => {
        fetchAll(onLocation, loc1, loc3, activeTab, chart)
    }, [onLocation])

    useEffect(() => {
       fetchAll(false, loc1, loc3, activeTab, chart) 
    }, [activeTab])

    return [onLocation, setOnLocation]
}

export default useFetchAll