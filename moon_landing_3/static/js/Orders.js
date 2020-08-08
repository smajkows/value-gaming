import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';

function preventDefault(event) {
  event.preventDefault();
}

const useStyles = makeStyles((theme) => ({
  seeMore: {
    marginTop: theme.spacing(3),
  },
}));

class Orders extends React.Component {

  render() {
    const holdings = this.props.my_hold;
    return (
        <React.Fragment>
          <Table size="medium" stickyHeader aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell>Ticker</TableCell>
                <TableCell>Avg. Price</TableCell>
                <TableCell># Shares</TableCell>
                <TableCell>Market Value</TableCell>
                <TableCell align="right">Today's Gain/Loss (%) </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {holdings.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.instrument.symbol}</TableCell>
                    <TableCell>{row.averagePrice}</TableCell>
                    <TableCell>{row.longQuantity}</TableCell>
                    <TableCell>{row.marketValue}</TableCell>
                    <TableCell align="right">{row.currentDayProfitLossPercentage}</TableCell>
                  </TableRow>
              ))}
            </TableBody>
          </Table>
        </React.Fragment>
    );
  }
}

export default Orders;