import React from 'react'

function WithFetchAll(WrappedComponent) {

    return class extends React.Component {

        constructor(props) {    
            super(props)
            this.state = {
                onLocation: false,
            }
            this.fetchAll = this.fetchAll.bind(this)
        }

       
        // fetch height and temperature info from all rides in db
        fetchAll(chart, onLocation, loc1, loc3, activeTab) {

            this.setState({ onLocation: onLocation })
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
       
        render() {
            return <WrappedComponent 
                fetchAll={this.fetchAll} 
                onLocation={this.state.onLocation}
                {...this.props} />
        }
    }
}

export default WithFetchAll