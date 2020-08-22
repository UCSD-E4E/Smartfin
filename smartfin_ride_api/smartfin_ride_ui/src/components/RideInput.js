import React, { useState } from 'react'

function RideInput() {
   
    const [rideId, setRideId] = useState('')
    const [data, setData] = useState('')
    
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
        console.log(rideId)
    }

    function handleSubmit(e) {
        e.preventDefault()
        console.log('submitted: ', rideId)

        if (rideId.length < 5) {
            console.log('please enter a valid ride id')
            return
        }

        let url = `http://127.0.0.1:8000/ride/ride-create/${rideId}/`

        fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(typeof(data))
            setData(JSON.stringify(data))
        })
        .catch(function(error){
            console.log('ERROR:', error)
        })

        setRideId('')
    } 

    
    return (
        <div>
            <form onSubmit={e => handleSubmit(e)}>
                <input type="text" onChange={e => handleChange(e)} value={rideId} />
                <input type="submit" value="Fetch Data" />
            </form>

            <div>{data}</div>
        </div>
    )
}

export default RideInput
