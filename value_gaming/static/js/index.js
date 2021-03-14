import React from "react";
import ReactDOM from "react-dom";
import Base from "./Base";


export default function Main() {
  return (
      <Base />
  );
}



const rootElement = document.getElementById("react");
ReactDOM.render(<Main />, rootElement);
