import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import SmartfinUI from './SmartfinUI';
import RideContextProvider from './contexts/RideContext';

ReactDOM.render(
  <React.StrictMode>
    <RideContextProvider>
      <SmartfinUI />
    </RideContextProvider>
  </React.StrictMode>,
  document.getElementById('root')
);

