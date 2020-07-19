import React from 'react'
import ReactDOM from 'react-dom'
import Dashboard from './Dashboard'


function Welcome(props) {
  return <Dashboard/>;
}

const element = <Welcome name="world" />;
ReactDOM.render(
  element,
  document.getElementById('react')
);