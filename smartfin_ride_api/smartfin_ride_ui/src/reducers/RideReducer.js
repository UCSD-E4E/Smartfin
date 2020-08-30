

function RideReducer(state, action) {

    switch(action.type) {
        case 'SET_RIDE_DATA':
            localStorage.setItem('15692', JSON.stringify(action.payload));
            return Object.assign({}, state, action.payload)
        default:
            return state
    }

}

export default RideReducer