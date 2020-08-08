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

const data = [
  createData('2020-01-01', 0),
  createData('2020-01-10', 300),
  createData('06:00', 600),
  createData('09:00', 800),
  createData('12:00', 1500),
  createData('15:00', 2000),
  createData('18:00', 2400),
  createData('21:00', 2400),
];

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
          <YAxis>
            <Label
              angle={270}
              position="left"
              style={{ textAnchor: 'middle', fill: null }}
            >
              Portfolio Value ($)
            </Label>
          </YAxis>
          <Line type="monotone" dataKey="amount" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </React.Fragment>
  );
  }
}

export default Chart;