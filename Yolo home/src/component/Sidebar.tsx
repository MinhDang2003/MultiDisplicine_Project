import { useState } from "react";
import { ProSidebar, Menu, MenuItem } from "react-pro-sidebar";
import { Box, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme.tsx";
import "react-pro-sidebar/dist/css/styles.css";
import { useNavigate, Link } from "react-router-dom";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import FaceIcon from '@mui/icons-material/Face';
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";
import LogoutIcon from '@mui/icons-material/Logout';
import useLogout from "../hooks/useLogout";
import KeyboardVoiceIcon from '@mui/icons-material/KeyboardVoice';

const Item = ({ title, to, icon, selected, setSelected }: { title: string; to: string; icon: JSX.Element; selected: string; setSelected: React.Dispatch<React.SetStateAction<string>> }) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    return (
        <MenuItem 
            active={selected === title}
            style={{
                color: colors.grey[100],
            }}
            onClick={() => setSelected(title)}
            icon={icon}
        >
            <Typography>{title}</Typography>
            <Link to={to} />
        </MenuItem>
    );
};

const Sidebarr = () => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [isCollapsed, setIsCollapsed] = useState(true);
    const [selected, setSelected] = useState("Home");
    const navigate = useNavigate();
    const logout = useLogout();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <Box className="shadow-lg"
            sx={{
                height: "100%",
                "& .pro-sidebar-inner": {
                    backgroundColor: "#FEFAF6!important",
                },
                "& .pro-icon-wrapper": {
                    backgroundColor: "transparent !important",
                },
                "& .pro-inner-item": {
                    padding: "5px 35px 5px 20px !important",
                },
                "& .pro-inner-item:hover": {
                    color: "#153448 !important",
                },
            }}
        >
            <ProSidebar collapsed={isCollapsed}>
                <Menu iconShape="square">
                    {/* LOGO AND MENU ICON */}
                    <MenuItem
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        icon={isCollapsed ? <MenuOutlinedIcon /> : undefined}
                        style={{
                            margin: "10px 0 20px 0",
                            color: colors.grey[100],
                        }}
                    >
                        {!isCollapsed && (
                            <Box
                                display="flex"
                                justifyContent="space-between"
                                alignItems="center"
                                ml="15px"
                            >
                                <Typography fontFamily={"Inter"} fontSize={30} color={colors.grey[100]}>
                                    YoloHome
                                </Typography>
                                <IconButton onClick={() => setIsCollapsed(!isCollapsed)}>
                                    <MenuOutlinedIcon />
                                </IconButton>
                            </Box>
                        )}
                    </MenuItem>

                    <Box paddingLeft={isCollapsed ? undefined : "10%"}>
                        <Item
                            title="Home"
                            to="/"
                            icon={<HomeOutlinedIcon />}
                            selected={selected}
                            setSelected={setSelected}
                        />
                        <Item
                            title="Dashboard"
                            to="/Dashboard"
                            icon={<BarChartOutlinedIcon />}
                            selected={selected}
                            setSelected={setSelected}
                        />
                        <Item
                            title="Facial verification"
                            to="/CamTest"
                            icon={<FaceIcon />}
                            selected={selected}
                            setSelected={setSelected}
                        />
                        <Item
                            title="Voice Recognition"
                            to="/Voice"
                            icon={<KeyboardVoiceIcon />}
                            selected={selected}
                            setSelected={setSelected}
                        />
                        <MenuItem
                            onClick={handleLogout}
                            icon={<LogoutIcon />}
                            style={{
                                color: colors.grey[100],
                            }}
                        >
                            <Typography>Logout</Typography>
                        </MenuItem>
                    </Box>
                </Menu>
            </ProSidebar>
        </Box>
    );
};

export default Sidebarr;
