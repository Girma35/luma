import React from "react";

export const Footer: React.FC = () => {
    return (
        <footer className="bg-primary/5 border-t border-primary/10 py-8 px-10 mt-10">
            <div className="max-w-[1200px] mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="flex items-center gap-2 opacity-50">
                    <div className="size-5">
                        <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                            <path
                                clipRule="evenodd"
                                d="M12.0799 24L4 19.2479L9.95537 8.75216L18.04 13.4961L18.0446 4H29.9554L29.96 13.4961L38.0446 8.75216L44 19.2479L35.92 24L44 28.7521L38.0446 39.2479L29.96 34.5039L29.9554 44H18.0446L18.04 34.5039L9.95537 39.2479L4 28.7521L12.0799 24Z"
                                fill="currentColor"
                                fillRule="evenodd"
                            />
                        </svg>
                    </div>
                    <span className="text-sm font-bold">ReOrder AI Dashboard</span>
                </div>
                <p className="text-[#6a7b7c] text-xs">© 2024 SupplyLogic Systems. All AI models patented.</p>
                <div className="flex gap-6">
                    <a className="text-xs text-[#6a7b7c] font-medium hover:text-primary transition-colors" href="#">
                        Documentation
                    </a>
                    <a className="text-xs text-[#6a7b7c] font-medium hover:text-primary transition-colors" href="#">
                        API Status
                    </a>
                    <a className="text-xs text-[#6a7b7c] font-medium hover:text-primary transition-colors" href="#">
                        Support
                    </a>
                </div>
            </div>
        </footer>
    );
};
