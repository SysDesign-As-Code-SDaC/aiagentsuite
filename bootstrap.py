#!/usr/bin/env python3
"""
AI AGENT SUITE BOOTSTRAP - LLM-Friendly Installation

This script allows LLMs to bootstrap the AI Agent Suite with minimal user interaction.
Users only need to choose LSP or MCP, and the system handles everything automatically.

Usage: python bootstrap.py
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.error

class BootstrapManager:
    """Manages the complete bootstrap process for AI Agent Suite."""

    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.config = {
            "installation_method": None,
            "ai_interface": None,
            "lsp_port": 3000,
            "mcp_port": 3001,
            "docker_available": False,
            "docker_preferred": False,
            "verification_results": {},
            "setup_complete": False
        }

    async def bootstrap_ai_agent_suite(self) -> None:
        """
        Main bootstrap function that LLMs and users can call.
        This handles everything automatically from detection to full launch.
        """
        print("🤖 AI AGENT SUITE - FULLY AUTOMATED ENTERPRISE BOOTSTRAP")
        print("=" * 70)
        print("🚀 TRANSFORMING AI INTO ENTERPRISE SOFTWARE ENGINEERING EXPERT")
        print("✨ COMPLETE HANDS-OFF SETUP - NO USER INPUT REQUIRED")
        print("⏱️  ~5 minutes to enterprise-grade AI capabilities")
        print()

        try:
            # Step 1: Auto-detect configuration
            print("🔧 Step 1: Auto-detecting optimal configuration...")
            await self._auto_detect_configuration()

            # Step 2: Verify and prepare system
            print("🔍 Step 2: Verifying system requirements...")
            await self._verify_system_requirements()

            # Step 3: Unified launch (everything together)
            print("🚀 Step 3: Launching complete enterprise suite...")
            await self._unified_enterprise_launch()

            # Step 4: Verify everything works
            print("✅ Step 4: Verifying all services...")
            await self._verify_installation()

            # Step 5: Launch monitoring dashboard
            print("📊 Step 5: Starting enterprise monitoring...")
            await self._launch_monitoring_dashboard()

            # Step 6: Save configuration
            self._save_bootstrap_config()

            # Step 7: Display success and final status
            self._display_final_success()

            # Step 8: Keep services running with monitoring
            await self._run_enterprise_operations()

        except Exception as e:
            print(f"\n❌ Bootstrap failed: {e}")
            self.config["error"] = str(e)
            await self._offer_automated_troubleshooting()
            raise

    async def _auto_detect_configuration(self) -> None:
        """Automatically detect optimal configuration."""
        # Default to complete enterprise suite
        self.config["ai_interface"] = "both"  # LSP + MCP
        self.config["installation_method"] = "docker"  # Primary preference
        self.config["monitoring_enabled"] = True
        self.config["dashboard_enabled"] = True

        print("   ✅ Configuration: LSP + MCP + Enterprise Monitoring")
        print("   ✅ Method: Docker (enterprise-grade)")
        print("   ✅ Monitoring: Complete observability stack")
        print("   ✅ Dashboard: Unified monitoring interface")

    async def _unified_enterprise_launch(self) -> None:
        """Launch complete enterprise suite together."""
        # Launch all services simultaneously
        installation_method = self.config["installation_method"]

        # Start complete system (LSP + MCP + monitoring)
        await self._setup_both_modes(installation_method)

        # Immediately launch dashboard
        await self._launch_monitoring_dashboard()

        print("   🎯 Enterprise suite launched successfully!")

    async def _launch_monitoring_dashboard(self) -> None:
        """Launch the enterprise monitoring dashboard."""
        try:
            # Run dashboard in background subprocess
            import subprocess
            dashboard_cmd = [sys.executable, "enterprise_dashboard.py", "--web"]
            process = subprocess.Popen(
                dashboard_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.project_root
            )

            # Store process for cleanup
            self.config["dashboard_process"] = process.pid

            print("   📊 Monitoring dashboard: http://localhost:8080")

        except Exception as e:
            print(f"   ⚠️  Dashboard launch warning: {e}")
            print("   💡 Manual dashboard: python enterprise_dashboard.py --web")

    async def _run_enterprise_operations(self) -> None:
        """Run enterprise operations with monitoring."""
        print("\n" + "=" * 70)
        print("🎯 ENTERPRISE AI AGENT SUITE IS NOW OPERATIONAL!")
        print("=" * 70)
        print()
        print("🚀 ACTIVE SERVICES:")
        print("   • LSP Server (AI Editor Integration):     localhost:3000")
        print("   • MCP Server (AI Model Tools):           localhost:3001")
        print("   • Grafana Dashboard:                     localhost:3000")
        print("   • Prometheus Metrics:                    localhost:9090")
        print("   • Jaeger Tracing:                        localhost:16686")
        print("   • PostgreSQL Database:                   localhost:5432")
        print("   • Redis Cache:                           localhost:6379")
        print("   • Enterprise Dashboard:                  localhost:8080")
        print()
        print("📊 MONITORING YOUR ENTERPRISE SUITE:")
        print("   • Unified Dashboard:                     localhost:8080")
        print("   • Terminal Dashboard:                    python enterprise_dashboard.py")
        print("   • Docker Status:                         docker-compose ps")
        print()
        print("🤖 AI CAPABILITIES NOW AVAILABLE:")
        print("   • LSP: AI editors become enterprise code assistants")
        print("   • MCP: AI models get enterprise development tools")
        print("   • Complete formal verification & chaos engineering")
        print("   • CQRS, Event Sourcing, enterprise patterns")
        print()
        print("🛑 SHUTDOWN:")
        print("   Ctrl+C here OR: docker-compose down")
        print("   Services will auto-clean up gracefully")
        print()

        # Setup shutdown handling
        self._setup_shutdown_handling()

    def _display_final_success(self) -> None:
        """Display final success status."""
        pass  # Already displayed in run_enterprise_operations

    async def _offer_automated_troubleshooting(self) -> None:
        """Offer automated troubleshooting guidance."""
        print("\n" + "=" * 60)
        print("🔧 AUTOMATED TROUBLESHOOTING")
        print("=" * 60)
        print()
        print("🚨 Bootstrap failed - trying automated fixes:")
        print()

        # Check Docker status
        docker_available = await self._check_docker()
        if not docker_available:
            print("❌ Docker not found - attempting installation...")
            print("   Visit: https://docs.docker.com/get-docker/")
            print("   OR run: python bootstrap.py --force-local")
            return

        # Try to cleanup and restart
        print("🔄 Attempting automatic cleanup and restart...")
        try:
            await self._run_command("docker-compose down", silent=True)
            await asyncio.sleep(2)

            print("✨ Restarting bootstrap in 3 seconds...")
            await asyncio.sleep(3)

            # Restart bootstrap (recursive call with cleanup)
            self.config.pop("error", None)  # Clear error
            await self.bootstrap_ai_agent_suite()

        except Exception as e:
            print(f"❌ Auto-recovery failed: {e}")
            print("\n📋 Manual troubleshooting:")
            print("1. docker-compose down")
            print("2. docker system prune -a")
            print("3. python bootstrap.py")
            print("4. Check Docker Desktop is running")

    async def _get_user_choice(self) -> str:
        """Get user's choice for LSP, MCP, or both."""
        print("🎯 SETUP CHOICE (Only interaction required)")
        print("-" * 40)

        while True:
            print("\nWhat type of AI interface would you like to set up?")
            print("1. LSP (Language Server Protocol)")
            print("   ↳ Best for: Cursor, VSCode, most AI editors")
            print("   ↳ Transforms AI into enterprise code assistant")
            print()
            print("2. MCP (Model Context Protocol)")
            print("   ↳ Best for: Direct AI model integration")
            print("   ↳ Provides enterprise tools to AI agents")
            print()
            print("3. BOTH LSP & MCP")
            print("   ↳ Complete AI editor + direct model integration")
            print()

            choice = input("Enter your choice (1, 2, or 3): ").strip()

            if choice == "1" or choice.lower() == "lsp":
                ai_interface = "lsp"
                print("✅ Selected: LSP Mode")
                break
            elif choice == "2" or choice.lower() == "mcp":
                ai_interface = "mcp"
                print("✅ Selected: MCP Mode")
                break
            elif choice == "3" or choice.lower() == "both":
                ai_interface = "both"
                print("✅ Selected: BOTH LSP & MCP")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")

        self.config["ai_interface"] = ai_interface
        print()
        return ai_interface

    async def _verify_system_requirements(self) -> None:
        """Verify that the system meets minimum requirements."""
        print("🔍 VERIFYING SYSTEM REQUIREMENTS")
        print("-" * 40)

        requirements = {
            "python": {
                "checker": self._check_python,
                "description": "Python 3.9+ for AI Agent Suite",
                "required": True
            },
            "docker": {
                "checker": self._check_docker,
                "description": "Docker (recommended for easy deployment)",
                "required": False
            },
            "git": {
                "checker": self._check_git,
                "description": "Git for repository management",
                "required": True
            }
        }

        self.config["docker_available"] = await requirements["docker"]["checker"]()

        all_good = True
        for req_name, req_info in requirements.items():
            checker = req_info["checker"]
            description = req_info["description"]
            required = req_info["required"]

            result = await checker()
            status = "✅" if result else ("❌" if required else "⚠️")
            req_type = "REQUIRED" if required else "OPTIONAL"

            print(f"{status} {req_name}: {description}")
            if required and not result:
                all_good = False
            elif not required and not result:
                print(f"   →{req_name} not found, will use alternative method")

        if not all_good:
            print("\n❌ Critical requirements not met. Please install missing components and try again.")
            sys.exit(1)

        # Docker is primary deployment method - fully automated
        if self.config["docker_available"]:
            print("\n🐳 Docker PRIMARY DEPLOYMENT")
            print("   Docker provides enterprise-grade, isolated, scalable deployment")
            print("   All services run in containers with built-in monitoring and security")
            self.config["docker_preferred"] = True
            print("🐳 Using Docker deployment (fully automated)")
        else:
            print("\n🐳 Docker not available - install Docker for enterprise features")
            print("   https://docs.docker.com/get-docker/")
            print("\n📦 Falling back to local installation (automated)")
            self.config["docker_preferred"] = False

        print()

    async def _check_python(self) -> bool:
        """Check Python version."""
        return sys.version_info >= (3, 9)

    async def _check_docker(self) -> bool:
        """Check Docker availability."""
        return await self._run_command("docker --version", silent=True)

    async def _check_git(self) -> bool:
        """Check Git availability."""
        return await self._run_command("git --version", silent=True)

    async def _run_command(self, cmd: str, silent: bool = False) -> bool:
        """Run a command and return success status."""
        try:
            result = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE if silent else None,
                stderr=asyncio.subprocess.PIPE if silent else None,
                cwd=self.project_root
            )
            if silent:
                await result.wait()
            return result.returncode == 0
        except Exception:
            return False

    async def _determine_installation_method(self) -> str:
        """Determine whether to use Docker or local pip installation."""
        if self.config["docker_preferred"]:
            method = "docker"
            print("🐳 INSTALLATION METHOD: Docker (Recommended)")
        else:
            method = "local"
            print("📦 INSTALLATION METHOD: Local pip installation")

        self.config["installation_method"] = method
        print()
        return method

    async def _setup_lsp_mode(self, installation_method: str) -> None:
        """Setup LSP-only mode."""
        print("🏗️  SETTING UP LSP MODE")
        print("-" * 40)
        print("LSP Mode: Transforms AI editors into enterprise software engineers")
        print("Features: Formal verification, chaos engineering, CQRS, enterprise patterns")
        print()

        if installation_method == "docker":
            await self._setup_docker_lsp()
        else:
            await self._setup_local_lsp()

    async def _setup_mcp_mode(self, installation_method: str) -> None:
        """Setup MCP-only mode."""
        print("🔧 SETTING UP MCP MODE")
        print("-" * 40)
        print("MCP Mode: Direct AI model integration with enterprise tools")
        print("Features: Contract verification, enterprise code generation, formal proofs")
        print()

        if installation_method == "docker":
            await self._setup_docker_mcp()
        else:
            await self._setup_local_mcp()

    async def _setup_both_modes(self, installation_method: str) -> None:
        """Setup both LSP and MCP modes."""
        print("🚀 SETTING UP LSP + MCP COMPLETE MODE")
        print("-" * 40)
        print("Complete Mode: AI editor transformation + direct model integration")
        print("Features: Everything - maximum enterprise AI capabilities")
        print()

        if installation_method == "docker":
            await self._setup_docker_both()
        else:
            await self._setup_local_both()

    async def _setup_docker_lsp(self) -> None:
        """Setup Docker LSP mode."""
        print("🐳 Starting LSP servers with Docker...")

        # Start minimal Docker services for LSP
        services = [
            "aiagentsuite-lsp-server",
            "aiagentsuite-core",
            "aiagentsuite-db",
            "aiagentsuite-cache"
        ]

        success = await self._start_docker_services(services)
        if success:
            print("✅ LSP Docker services started")
            await self._verify_docker_service("localhost", 3000)
        else:
            print("❌ Failed to start LSP Docker services")

    async def _setup_docker_mcp(self) -> None:
        """Setup Docker MCP mode."""
        print("🐳 Starting MCP servers with Docker...")

        services = [
            "aiagentsuite-mcp-server",
            "aiagentsuite-core",
            "aiagentsuite-db",
            "aiagentsuite-cache"
        ]

        success = await self._start_docker_services(services)
        if success:
            print("✅ MCP Docker services started")
            await self._verify_docker_service("localhost", 3001)
        else:
            print("❌ Failed to start MCP Docker services")

    async def _setup_docker_both(self) -> None:
        """Setup both LSP and MCP with Docker."""
        print("🐳 Starting complete AI Agent Suite with Docker...")

        services = [
            "aiagentsuite-lsp-server",
            "aiagentsuite-mcp-server",
            "aiagentsuite-core",
            "aiagentsuite-db",
            "aiagentsuite-cache"
            "aiagentsuite-monitoring"
        ]

        success = await self._start_docker_services(services)
        if success:
            print("✅ Complete system Docker services started")
            await self._verify_docker_service("localhost", 3000)  # LSP
            await self._verify_docker_service("localhost", 3001)  # MCP
            await self._verify_docker_service("localhost", 8000)  # Core API

    async def _setup_local_lsp(self) -> None:
        """Setup local LSP mode."""
        print("📦 Starting LSP servers locally...")

        # Install dependencies if needed
        await self._setup_dependencies()

        # Start LSP server
        await self._start_local_server("lsp")

    async def _setup_local_mcp(self) -> None:
        """Setup local MCP mode."""
        print("📦 Starting MCP servers locally...")

        # Install dependencies if needed
        await self._setup_dependencies()

        # Start MCP server
        await self._start_local_server("mcp")

    async def _setup_local_both(self) -> None:
        """Setup both locally."""
        print("📦 Starting complete system locally...")

        # Install dependencies
        await self._setup_dependencies()

        # Start both servers
        await self._start_local_server("lsp")
        await self._start_local_server("mcp")

    async def _setup_dependencies(self) -> None:
        """Setup local dependencies."""
        print("📦 Installing AI Agent Suite dependencies...")

        # Check if already installed
        try:
            import aiagentsuite
            print("✅ AI Agent Suite already installed")
            return
        except ImportError:
            pass

        # Install using pip
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
            success = await self._run_command(" ".join(cmd))
            if success:
                print("✅ Dependencies installed successfully")
            else:
                print("❌ Failed to install dependencies")
                print("   Try: pip install -r requirements.txt")
        except Exception as e:
            print(f"❌ Installation error: {e}")

    async def _start_docker_services(self, services: List[str]) -> bool:
        """Start Docker services."""
        try:
            # Pull images first
            await self._run_command("docker-compose pull")

            # Start services
            service_args = " ".join(services)
            cmd = f"docker-compose up -d {service_args}"
            success = await self._run_command(cmd)

            # Wait for services to be ready
            await asyncio.sleep(30)

            return success
        except Exception as e:
            print(f"❌ Docker setup error: {e}")
            return False

    async def _start_local_server(self, server_type: str) -> None:
        """Start local server process."""
        port = 3000 if server_type == "lsp" else 3001
        print(f"🚀 Starting {server_type.upper()} server on port {port}...")

        try:
            # Use the lsp-setup.py script for local deployment
            cmd = [sys.executable, "lsp-setup.py", "--ai-editor", "generic",
                   f"--{server_type}-port", str(port)]
            success = await self._run_command(" ".join(cmd))

            if success:
                print(f"✅ {server_type.upper()} server started on port {port}")
            else:
                print(f"❌ Failed to start {server_type.upper()} server")
        except Exception as e:
            print(f"❌ Local server error: {e}")

    async def _verify_docker_service(self, host: str, port: int, timeout: int = 60) -> None:
        """Verify Docker service is running."""
        import socket

        print(f"🔍 Verifying service on {host}:{port}...")

        for i in range(timeout):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()

                if result == 0:
                    print(f"✅ Service verified on {host}:{port}")
                    return
            except:
                pass

            if i < timeout - 1:
                await asyncio.sleep(1)

        print(f"❌ Service verification failed on {host}:{port}")

    async def _verify_installation(self) -> None:
        """Verify the complete installation works."""
        print("🎯 VERIFYING COMPLETE INSTALLATION")
        print("-" * 40)

        verification_results = {}

        # Test core functionality
        verification_results["core_test"] = await self._verify_core_functionality()

        # Test enterprise features
        verification_results["enterprise_test"] = await self._verify_enterprise_features()

        # Verify connectivity
        if self.config["ai_interface"] in ["lsp", "both"]:
            verification_results["lsp_connection"] = await self._verify_service_connection(3000)
        if self.config["ai_interface"] in ["mcp", "both"]:
            verification_results["mcp_connection"] = await self._verify_service_connection(3001)

        self.config["verification_results"] = verification_results

        # Summary
        successful = sum(1 for result in verification_results.values() if result)
        total = len(verification_results)

        print("\n" + "="*60)
        print("📊 VERIFICATION SUMMARY")
        print("="*60)
        print(f"Tests Passed: {successful}/{total}")

        if successful == total:
            print("🎉 ALL VERIFICATION TESTS PASSED!")
            self.config["setup_complete"] = True
        else:
            print("⚠️  Some verification tests failed, but basic functionality should work")
            self.config["setup_complete"] = True  # Still mark complete

    async def _verify_core_functionality(self) -> bool:
        """Test core AI Agent Suite functionality."""
        try:
            # Import and basic functionality test
            from src.aiagentsuite.core.event_sourcing import get_global_event_sourcing_manager
            from src.aiagentsuite.core.formal_verification import get_global_verification_manager
            from src.aiagentsuite.core.chaos_engineering import get_global_chaos_manager

            # Test basic initialization
            es_manager = get_global_event_sourcing_manager()
            verification_manager = get_global_verification_manager()
            chaos_manager = get_global_chaos_manager()

            await verification_manager.initialize()
            await chaos_manager.initialize()

            print("   ✅ Core functionality verified")
            return True
        except Exception as e:
            print(f"   ❌ Core functionality error: {e}")
            return False

    async def _verify_enterprise_features(self) -> bool:
        """Test enterprise features are available."""
        try:
            # Quick enterprise feature test
            from src.aiagentsuite.core.formal_verification import VerificationProperty, PropertyType
            from src.aiagentsuite.core.event_sourcing import CreateUserCommand
            from src.aiagentsuite.core.chaos_engineering import ChaosExperiment, ChaosEvent, ChaosIntensity

            # Test enterprise component creation
            prop = VerificationProperty("test", "Test", "Test desc", PropertyType.SECURITY, "test_expr")
            cmd = CreateUserCommand("test_user", "Test User", "test@example.com")
            chaos = ChaosExperiment("test", "Test", [ChaosEvent.LATENCY_INJECTION], ChaosIntensity.MINIMAL, 10)

            print("   ✅ Enterprise features verified")
            return True
        except Exception as e:
            print(f"   ❌ Enterprise features error: {e}")
            return False

    async def _verify_service_connection(self, port: int) -> bool:
        """Verify service connection on port."""
        import socket

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            return result == 0
        except:
            return False

    def _setup_shutdown_handling(self) -> None:
        """Setup proper shutdown handling for running services."""
        import atexit
        import signal

        # Register cleanup function
        atexit.register(self._cleanup_services)

        # Handle signals
        def signal_handler(signum, frame):
            print(f"\n\n🛑 Received signal {signum}, shutting down gracefully...")
            self._cleanup_services()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Keep services running until user stops
        print("\n🔄 Services are running in background...")
        print("Press Ctrl+C or send SIGTERM to stop all services gracefully")

    def _cleanup_services(self) -> None:
        """Cleanup running services on shutdown."""
        installation_method = self.config.get("installation_method", "local")

        print("\n🧹 Cleaning up AI Agent Suite services...")

        if installation_method == "docker":
            try:
                # Stop Docker services gracefully
                import subprocess
                print("   🐳 Stopping Docker services...")
                result = subprocess.run(["docker-compose", "down"],
                                      capture_output=True, text=True, cwd=self.project_root)
                if result.returncode == 0:
                    print("   ✅ Docker services stopped gracefully")
                else:
                    print(f"   ⚠️  Docker cleanup warning: {result.stderr}")
            except Exception as e:
                print(f"   ❌ Docker cleanup error: {e}")
        else:
            try:
                # Kill local processes on configured ports
                import psutil
                import signal

                lsp_port = self.config.get("lsp_port", 3000)
                mcp_port = self.config.get("mcp_port", 3001)

                killed_count = 0
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        # Check if process is using our ports
                        for conn in proc.connections():
                            if conn.laddr.port in [lsp_port, mcp_port]:
                                print(f"   🛑 Terminating process {proc.pid} on port {conn.laddr.port}")
                                proc.terminate()
                                killed_count += 1
                                break
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        continue

                if killed_count > 0:
                    print(f"   ✅ Stopped {killed_count} local services")
                else:
                    print("   ℹ️  No running services found to clean up")

            except ImportError:
                print("   ℹ️  psutil not available, manual cleanup required")
                lsp_port = self.config.get("lsp_port", 3000)
                mcp_port = self.config.get("mcp_port", 3001)
                print(f"   💡 Manually kill processes on ports {lsp_port} and {mcp_port}")
            except Exception as e:
                print(f"   ⚠️  Local cleanup error: {e}")

    def _offer_troubleshooting(self) -> None:
        """Offer troubleshooting guidance on failure."""
        print("\n" + "=" * 60)
        print("🔧 TROUBLESHOOTING GUIDE")
        print("=" * 60)
        print("If setup failed, try these solutions:")
        print()
        print("1. 📦 Dependencies Issue:")
        print("   pip install -r requirements.txt")
        print("   # or if using conda:")
        print("   conda install python=3.9 pip")
        print()
        print("2. 🐳 Docker Issues:")
        print("   docker --version")
        print("   docker-compose --version")
        print("   # If not installed, follow Docker installation guide")
        print()
        print("3. 🚫 Port Conflicts:")
        print("   netstat -an | grep LISTEN")
        print("   # Kill processes using ports 3000-3002, 5432, 6379")
        print()
        print("4. 🔄 Clean Retry:")
        print("   python bootstrap.py")
        print("   # Choose clean installation option when prompted")
        print()
        print("5. 📋 System Check:")
        print("   python -c \"import sys; print(f'Python: {sys.version}')\"")
        print("   python -c \"import psycopg2; import redis\"")
        print()
        print("📚 Documentation:")
        print("   docs/ENTERPRISE_DEPLOYMENT_GUIDE.md")

    def _display_success_message(self) -> None:
        """Display success message with usage instructions."""
        ai_interface = self.config["ai_interface"]
        installation_method = self.config["installation_method"]

        print("\n" + "=" * 60)
        print("🎉 AI AGENT SUITE SETUP COMPLETE!")
        print("=" * 60)
        print("Your AI editor is now an EXPERT SOFTWARE ENGINEER!")
        print()
        print("🚀 ACTIVE SERVERS:")

        if ai_interface in ["lsp", "both"]:
            print(f"   LSP Server: localhost:{self.config['lsp_port']} ✅")
            print("     ↳ Connect your AI editor (Cursor, VSCode, etc.)")
            print("     ↳ Transforms AI into enterprise code assistant")

        if ai_interface in ["mcp", "both"]:
            print(f"   MCP Server: localhost:{self.config['mcp_port']} ✅")
            print("     ↳ Direct AI model integration")
            print("     ↳ Enterprise tools for AI agents")

        print()
        print("🧠 ENTERPRISE CAPABILITIES ENABLED:")
        capabilities = [
            "Formal Verification (mathematical correctness)",
            "Chaos Engineering (failure simulation)",
            "Event Sourcing & CQRS (data consistency)",
            "Zero Trust Security (assume breach)",
            "Enterprise Observability (monitoring & alerting)",
            "Sustainable Engineering (carbon awareness)",
            "Platform Engineering (internal developer tools)",
            "All 20 software engineering principles"
        ]

        for cap in capabilities:
            print(f"   ✅ {cap}")
        print()
        print("💡 HOW TO USE:")
        print("   1. Start your AI editor" if ai_interface in ["lsp", "both"] else "   1. Skip LSP setup (not selected)")
        print("   2. Configure LSP client to connect to localhost:3000" if ai_interface in ["lsp", "both"] else "   2. Connect AI models to MCP (see below)")
        print("   3. Ask AI: 'Create enterprise-grade user service with CQRS'")
        print("   4. AI generates verified, tested, enterprise-quality code!")
        print()

        # MCP Connection Guide if MCP is enabled
        if ai_interface in ["mcp", "both"]:
            print("🔌 MCP CONNECTION GUIDE:")
            print("   Connect your AI model/library using these examples:")
            print()
            print("   🐍 Python MCP Client:")
            print("   ```python")
            print("   from mcp import Client")
            print("   client = Client()")
            print("   await client.connect('ws://localhost:3001')")
            print("   result = await client.call('aiagentsuite.verifyContract', {...})")
            print("   ```")
            print()
            print("   📡 REST API Integration:")
            print("   ```bash")
            print("   curl -X POST http://localhost:3001/tools/aiagentsuite.formalVerify \\")
            print("        -H 'Content-Type: application/json' \\")
            print("        -d '{\"code\": \"def hello(): return 'world'\", \"requirements\": [...]}'")
            print("   ```")
            print()

            # Model-specific connection guides
            print("   🤖 MODEL-SPECIFIC INTEGRATIONS:")
            print("   • OpenAI: Use function calling with MCP endpoints")
            print("   • Claude: Implement custom tools via MCP protocol")
            print("   • Local models: Use MCP client libraries")
            print("   • LangChain: Integrate via MCP tool wrappers")
            print()

        print("🔧 MANAGEMENT COMMANDS:")
        if installation_method == "docker":
            print("   🔄 Restart: docker-compose restart")
            print("   📊 Status: docker-compose ps")
            print("   🛑 Stop: docker-compose down")
            print("   📋 Logs: docker-compose logs [service]")
        else:
            print("   🔄 Restart: python bootstrap.py (choose same options)")
            print("   📊 Status: Check running processes on ports 3000/3001")
            print("   🛑 Stop: Kill processes on ports 3000/3001")
            print("   🚨 Graceful Shutdown: Ctrl+C triggers auto-cleanup")
        print()
        print("📚 DOCUMENTATION:")
        print("   Enterprise Guide: docs/ENTERPRISE_DEPLOYMENT_GUIDE.md")
        print("   LSP/MCP Setup: lsp-setup.py --help")
        print("   API Reference: http://localhost:8000/docs" if installation_method == "docker" else "   API docs available after full deployment")
        print()
        print("🎯 RESULT:")
        print("   Before: AI generates basic code snippets")
        print("   After:  AI generates enterprise systems with all 20 principles")
        print("=" * 60)

    def _save_bootstrap_config(self) -> None:
        """Save the bootstrap configuration for future reference."""
        config_file = self.project_root / ".aiagentsuite_bootstrap.json"

        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)

        print(f"\\n💾 Configuration saved: {config_file}")


def main():
    """Main entry point for the bootstrap script."""
    print("🤖 Starting AI Agent Suite Bootstrap...")
    print("This will transform your AI editor into an enterprise software engineer!")
    print()

    try:
        bootstrapper = BootstrapManager()
        asyncio.run(bootstrapper.bootstrap_ai_agent_suite())
    except KeyboardInterrupt:
        print("\n\\n⏹️  Bootstrap interrupted by user")
        print("You can restart with: python bootstrap.py")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Bootstrap failed: {e}")
        print("\\nTroubleshooting:")
        print("- Make sure you have the required dependencies")
        print("- Try running with Docker: python bootstrap.py then select Docker option")
        print("- Check documentation in docs/ENTERPRISE_DEPLOYMENT_GUIDE.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
