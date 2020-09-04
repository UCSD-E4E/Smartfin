
function fetchRide(rideId, dispatch) {

    if (rideId < 5) {
        console.log('please enter a valid ride id')
        return
    }

    let url = `http://127.0.0.1:8000/ride/ride-create/${rideId}/`

    // fetch data of ride inputted
    fetch(url)
    .then(response => response.json())
    .then(data => {
        dispatch({
            type: 'SET_RIDE_DATA',
            payload: {
                rideId: data['rideId'],
                loc1: data['loc1'],
                loc3: data['loc3'],
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
    })
    .catch(function(error){
        console.log('ERROR:', error)
    })
} 


function useFetchRide() {
    return fetchRide
}

export default useFetchRide