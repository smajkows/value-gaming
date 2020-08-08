import React from 'react';
import { useTheme } from '@material-ui/core/styles';
import { LineChart, Line, XAxis, YAxis, Label, ResponsiveContainer } from 'recharts';
import Title from './Title';
import CurrencyFormat from "react-currency-format";
import TableCell from "@material-ui/core/TableCell";

// Generate Sales Data
function createData(time, amount) {
  return { time, amount };
}

class Chart extends React.Component {

  render() {
  return (
    <React.Fragment>
      <Title>Today: {this.props.daily_gain} </Title>
      <ResponsiveContainer>
        <LineChart
          data={this.props.chartdata}
          margin={{
            top: 16,
            right: 16,
            bottom: 0,
            left: 24,
          }}
        >
          <XAxis dataKey="time"/>
          <YAxis domain={['auto', 'auto']}>
            <Label
              angle={270}
              position="left"
              style={{ textAnchor: 'middle', fill: null }}
            >
              Portfolio Value ($)
            </Label>
          </YAxis>
          <Line type="monotone" dataKey="amount" dot={true} />
        </LineChart>
      </ResponsiveContainer>
    </React.Fragment>
  );
  }
}

export default Chart;