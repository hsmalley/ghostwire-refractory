#!/usr/bin/env python3
"""
# ⚡️ Llamafile Deployment Script

Deploy llamafiles as systemd units on remote hosts via SSH.
Supports Fabric for SSH management and Mitogen for performance enhancement.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from fabric import Connection
    from invoke import Responder
except ImportError:
    print("❌ Error: fabric library not found. Install with: pip install fabric")
    sys.exit(1)

from ghostwire.config.settings import settings


# Set up logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LlamaDeploymentError(Exception):
    """Custom exception for llama deployment errors."""
    pass


class LlamaDeployer:
    """Handles deployment of llamafiles to remote hosts via SSH."""
    
    def __init__(self, hosts: List[str], user: str = None, port: int = 22):
        """
        Initialize the deployer with target hosts.
        
        Args:
            hosts: List of hostnames/IP addresses to deploy to
            user: SSH username (defaults to current user)
            port: SSH port (defaults to 22)
        """
        self.hosts = hosts
        self.user = user or os.getenv("USER", "ubuntu")
        self.port = port
        logger.info(f"🦙 Initializing LlamaDeployer for {len(hosts)} hosts")
    
    def deploy_llamafile(
        self,
        llamafile_path: str,
        service_name: str = "llamafile",
        destination_path: str = "/opt/llamafiles",
        force: bool = False
    ) -> bool:
        """
        Deploy a llamafile to all configured hosts.
        
        Args:
            llamafile_path: Local path to the llamafile to deploy
            service_name: Name for the systemd service
            destination_path: Remote path to deploy llamafiles to
            force: If True, redeploy even if service already exists
            
        Returns:
            True if deployment succeeded on all hosts, False otherwise
        """
        logger.info(f"🚀 Deploying llamafile '{llamafile_path}' as service '{service_name}'")
        
        # Check if llamafile exists
        if not os.path.exists(llamafile_path):
            logger.error(f"❌ Llamafile not found: {llamafile_path}")
            return False
        
        # Get file info
        file_size = os.path.getsize(llamafile_path)
        logger.info(f"📊 Llamafile size: {file_size} bytes")
        
        success_count = 0
        for host in self.hosts:
            try:
                if self._deploy_to_host(host, llamafile_path, service_name, destination_path, force):
                    success_count += 1
                    logger.info(f"✅ Successfully deployed to {host}")
                else:
                    logger.error(f"❌ Failed to deploy to {host}")
            except Exception as e:
                logger.error(f"💥 Error deploying to {host}: {e}")
        
        logger.info(f"🏁 Deployment complete: {success_count}/{len(self.hosts)} hosts successful")
        return success_count == len(self.hosts)
    
    def _deploy_to_host(
        self,
        host: str,
        llamafile_path: str,
        service_name: str,
        destination_path: str,
        force: bool
    ) -> bool:
        """
        Deploy llamafile to a single host.
        
        Args:
            host: Hostname/IP address to deploy to
            llamafile_path: Local path to the llamafile to deploy
            service_name: Name for the systemd service
            destination_path: Remote path to deploy llamafiles to
            force: If True, redeploy even if service already exists
            
        Returns:
            True if deployment succeeded, False otherwise
        """
        logger.info(f"📡 Connecting to {host}...")
        
        # Create SSH connection
        conn = Connection(
            host=host,
            user=self.user,
            port=self.port,
            connect_kwargs={
                "key_filename": os.getenv("SSH_KEY_PATH"),
            } if os.getenv("SSH_KEY_PATH") else {}
        )
        
        try:
            # Check if service already exists (unless force is True)
            if not force:
                result = conn.run(f"systemctl is-active {service_name}", warn=True)
                if result.return_code == 0:
                    logger.warning(f"⚠️ Service '{service_name}' already active on {host}. Use --force to redeploy.")
                    return True
            
            # Create destination directory
            logger.info(f"📁 Creating destination directory: {destination_path}")
            conn.sudo(f"mkdir -p {destination_path}")
            conn.sudo(f"chown {self.user}:{self.user} {destination_path}")
            
            # Upload llamafile
            remote_llamafile_path = os.path.join(destination_path, os.path.basename(llamafile_path))
            logger.info(f"📤 Uploading llamafile to {remote_llamafile_path}")
            conn.put(llamafile_path, remote_llamafile_path)
            
            # Make llamafile executable
            logger.info("🔧 Making llamafile executable")
            conn.run(f"chmod +x {remote_llamafile_path}")
            
            # Create systemd unit file
            logger.info("📝 Creating systemd unit file")
            unit_content = self._generate_systemd_unit(service_name, remote_llamafile_path)
            unit_file_path = f"/etc/systemd/system/{service_name}.service"
            conn.run(f"echo '{unit_content}' | sudo tee {unit_file_path}")
            
            # Reload systemd and enable/start service
            logger.info("⚡ Reloading systemd and starting service")
            conn.sudo("systemctl daemon-reload")
            conn.sudo(f"systemctl enable {service_name}")
            conn.sudo(f"systemctl restart {service_name}")
            
            # Verify service is running
            logger.info("🔍 Verifying service status")
            result = conn.run(f"systemctl is-active {service_name}", warn=True)
            if result.return_code == 0 and result.stdout.strip() == "active":
                logger.info(f"✅ Service '{service_name}' is active on {host}")
                return True
            else:
                logger.error(f"❌ Service '{service_name}' failed to start on {host}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Failed to deploy to {host}: {e}")
            return False
        finally:
            conn.close()
    
    def _generate_systemd_unit(self, service_name: str, llamafile_path: str) -> str:
        """
        Generate systemd unit file content for the llamafile service.
        
        Args:
            service_name: Name for the systemd service
            llamafile_path: Path to the llamafile on the remote host
            
        Returns:
            Systemd unit file content as string
        """
        unit_content = f"""[Unit]
Description=Llamafile Service - {service_name}
After=network.target

[Service]
Type=simple
User={self.user}
ExecStart={llamafile_path} --server --port 8080
Restart=always
RestartSec=10
WorkingDirectory=/opt/llamafiles

[Install]
WantedBy=multi-user.target
"""
        return unit_content
    
    def check_health(self, service_name: str = "llamafile", port: int = 8080) -> dict:
        """
        Check health of deployed llamafile services.
        
        Args:
            service_name: Name of the systemd service to check
            port: Port on which the llamafile service is running
            
        Returns:
            Dictionary with health status for each host
        """
        import requests
        
        logger.info(f"🏥 Checking health of '{service_name}' service on port {port}")
        health_status = {}
        
        for host in self.hosts:
            try:
                # Try to reach the health endpoint
                url = f"http://{host}:{port}/health"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    health_status[host] = {"status": "healthy", "response": response.json()}
                    logger.info(f"✅ {host} is healthy")
                else:
                    health_status[host] = {"status": "unhealthy", "response": response.text}
                    logger.warning(f"⚠️ {host} returned status {response.status_code}")
            except Exception as e:
                health_status[host] = {"status": "unreachable", "error": str(e)}
                logger.error(f"❌ {host} is unreachable: {e}")
        
        return health_status


def main():
    """Main entry point for the llama deployment script."""
    parser = argparse.ArgumentParser(
        prog="llama_deploy",
        description="Deploy llamafiles as systemd units on remote hosts via SSH",
        epilog="""
Examples:
  %(prog)s --hosts server1,server2 --llamafile ~/models/llama3.llamafile
  %(prog)s --hosts server1 --llamafile ~/models/llama3.llamafile --service-name llama3-model
  %(prog)s --hosts server1 --check-health
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--hosts",
        type=str,
        required=True,
        help="Comma-separated list of hosts to deploy to (e.g., server1,server2,server3)"
    )
    
    parser.add_argument(
        "--llamafile",
        type=str,
        help="Path to the llamafile to deploy"
    )
    
    parser.add_argument(
        "--service-name",
        type=str,
        default="llamafile",
        help="Name for the systemd service (default: llamafile)"
    )
    
    parser.add_argument(
        "--destination-path",
        type=str,
        default="/opt/llamafiles",
        help="Remote path to deploy llamafiles to (default: /opt/llamafiles)"
    )
    
    parser.add_argument(
        "--user",
        type=str,
        help="SSH username (defaults to current user)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=22,
        help="SSH port (default: 22)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force redeployment even if service already exists"
    )
    
    parser.add_argument(
        "--check-health",
        action="store_true",
        help="Check health of deployed services instead of deploying"
    )
    
    parser.add_argument(
        "--health-port",
        type=int,
        default=8080,
        help="Port to check for health endpoint (default: 8080)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse hosts
    hosts = [host.strip() for host in args.hosts.split(",") if host.strip()]
    if not hosts:
        logger.error("❌ No valid hosts provided")
        sys.exit(1)
    
    # Create deployer
    deployer = LlamaDeployer(hosts=hosts, user=args.user, port=args.port)
    
    if args.check_health:
        # Check health of deployed services
        health_status = deployer.check_health(
            service_name=args.service_name,
            port=args.health_port
        )
        
        print("\\n🏥 Health Check Results:")
        print("=" * 50)
        for host, status in health_status.items():
            print(f"{host}: {status['status']}")
            if 'response' in status:
                print(f"  Response: {status['response']}")
            if 'error' in status:
                print(f"  Error: {status['error']}")
        print("=" * 50)
        
        # Check if all hosts are healthy
        unhealthy_count = sum(1 for status in health_status.values() 
                            if status['status'] != 'healthy')
        if unhealthy_count > 0:
            print(f"⚠️ {unhealthy_count} hosts are not healthy")
            sys.exit(1)
        else:
            print("✅ All hosts are healthy")
            sys.exit(0)
    
    else:
        # Deploy llamafile
        if not args.llamafile:
            logger.error("❌ --llamafile is required for deployment")
            sys.exit(1)
        
        if not os.path.exists(args.llamafile):
            logger.error(f"❌ Llamafile not found: {args.llamafile}")
            sys.exit(1)
        
        success = deployer.deploy_llamafile(
            llamafile_path=args.llamafile,
            service_name=args.service_name,
            destination_path=args.destination_path,
            force=args.force
        )
        
        if success:
            print("\\n🎉 Llamafile deployment successful!")
            print("💡 You can check service status with:")
            print(f"   systemctl status {args.service_name}")
            print("💡 Or check health with:")
            print(f"   {parser.prog} --hosts {','.join(hosts)} --check-health --service-name {args.service_name}")
            sys.exit(0)
        else:
            print("\\n💥 Llamafile deployment failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()