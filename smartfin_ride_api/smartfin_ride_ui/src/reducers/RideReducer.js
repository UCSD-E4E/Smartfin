

function RideReducer(state, action) {

    console.log('reducing')

    switch(action.type) {
        case 'SET_RIDE_DATA':
            return Object.assign({}, state, action.payload)
        default:
            return state
    }

}

export default RideReducer