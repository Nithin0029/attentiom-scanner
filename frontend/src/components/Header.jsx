function Header({ activeTab, onTabChange, children }) {
    return (
        <header className="header">
            <div>
                <p className="eyebrow">AI-POWERED MONITORING</p>
                <h1>Attention Scanner</h1>
                <p className="subtitle">
                    Real-time engagement and behavior analysis
                </p>
            </div>

            <div className="header-right">
                {children}

                <nav className="tab-nav">
                    <button
                        type="button"
                        className={`tab-button ${
                            activeTab === "monitor" ? "active" : ""
                        }`}
                        onClick={() => onTabChange("monitor")}
                    >
                        Live Monitor
                    </button>

                    <button
                        type="button"
                        className={`tab-button ${
                            activeTab === "history" ? "active" : ""
                        }`}
                        onClick={() => onTabChange("history")}
                    >
                        Session History
                    </button>
                </nav>
            </div>
        </header>
    );
}

export default Header;
