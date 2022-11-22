import * as React from "react";
//@ts-ignore
import { css } from "@emotion/css";

// @ts-ignore
import Button from "../components/Button/Button.jsx";
// @ts-ignore
import Group from "../components/Group/Group.jsx";
// @ts-ignore
import Icon from "../components/Icon/Icon.jsx";
// @ts-ignore
import Section from "../components/Section/Section.jsx";
// @ts-ignore
import Text from "../components/Text/Text.jsx";

import {Reader} from "@stripe/terminal-js";

const ConnectionInfo: React.FunctionComponent<{ reader: Reader, onClickDisconnect: any }> = (props): JSX.Element => {
    let content = props.reader ? (
        <Group
            direction="row"
            alignment={{
                justifyContent: "space-between",
                alignItems: "center"
            }}
        >
            <Group direction="row">
                <span>
                  <Icon icon="keypad"/>
                </span>
                <Text truncate color="dark" size={14}>
                    {props.reader.label}
                </Text>
            </Group>
            <Button color="text" onClick={props.onClickDisconnect}>
                Disconnect
            </Button>
        </Group>
    ) : (
        <Group direction="row">
              <span>
                <Icon icon="keypad"/>
              </span>
            <Text color="lightGrey" size={14}>
                No reader connected
            </Text>
        </Group>
    )

    return <Group direction="column" spacing={0}>
        <Section position="last">
            {content}
        </Section>
    </Group>
};

export default ConnectionInfo