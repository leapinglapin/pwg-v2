//@flow

import * as React from "react";

import DiscoverReaders from "./DiscoverReaders.jsx";

class Readers extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      mode: "list"
    };
  }


  handleSwitchToDiscover = () => {
    this.setState({ mode: "list" });
  };

  render() {
    const { mode } = this.state;

    const {
      readers,
      onClickDiscover,
      onClickCancelDiscover,
      onConnectToReader,
      handleUseSimulator
    } = this.props;
    switch (mode) {
      case "list":
        return (
          <DiscoverReaders
            onClickDiscover={onClickDiscover}
            onClickCancelDiscover={onClickCancelDiscover}
            onConnectToReader={onConnectToReader}
            readers={readers}
            handleUseSimulator={handleUseSimulator}
          />
        );
      default:
        return null;
    }
  }
}

export default Readers;
