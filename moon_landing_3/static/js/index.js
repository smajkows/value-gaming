import React from 'react'
import ReactDOM from 'react-dom'
import Base from './Base'


function Welcome(props)  {
  return <Base/>;
}

const element = <Welcome/>;

ReactDOM.render(
  element,
  document.getElementById('react')
);