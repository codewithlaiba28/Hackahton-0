#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo MCP Server Integration - GOLD TIER
Personal AI Employee Hackathon 0

Integrates with Odoo Community Edition via JSON-RPC API.
Supports: Invoice creation, Payment recording, Financial reporting

Reference: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html

Usage:
    python odoo_mcp.py --action create_invoice --customer "Client Name" --amount 1000
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')


class OdooMCP:
    """Odoo Model Context Protocol Server."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.accounting_folder = self.vault_path / 'Accounting'
        self.logs = self.vault_path / 'Logs'
        self.pending = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        # Create folders
        for folder in [self.accounting_folder, self.logs, self.pending, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Odoo Configuration - Hackathon Database
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'hackathon')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'antigravityuser18@gmail.com')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'Laiba@28july2007')
        
        self.authenticated = False
        self.uid = None
        
        # Try to authenticate
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Odoo via JSON-RPC."""
        try:
            url = f'{self.odoo_url}/web/session/authenticate'
            payload = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'db': self.odoo_db,
                    'login': self.odoo_username,
                    'password': self.odoo_password
                },
                'id': 1
            }
            
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            if result.get('result', {}).get('uid'):
                self.uid = result['result']['uid']
                self.authenticated = True
                print(f"[OK] Authenticated with Odoo (UID: {self.uid})")
                return True
            else:
                print("[WARN] Odoo authentication failed")
                return False
                
        except Exception as e:
            print(f"[WARN] Could not connect to Odoo: {e}")
            print("       Running in demo mode...")
            return False
    
    def _json_rpc_call(self, model: str, method: str, args: list = None, kwargs: dict = None) -> dict:
        """Make a JSON-RPC call to Odoo."""
        if not self.authenticated:
            return {'error': 'Not authenticated'}
        
        try:
            url = f'{self.odoo_url}/web/dataset/call'
            payload = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'model': model,
                    'method': method,
                    'args': args or [],
                    'kwargs': kwargs or {}
                },
                'id': 1
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.json()
            
        except Exception as e:
            return {'error': str(e)}
    
    def create_invoice(
        self,
        customer_name: str,
        amount: float,
        description: str = "Invoice",
        auto_post: bool = False
    ) -> Dict[str, Any]:
        """
        Create an invoice in Odoo.
        
        Args:
            customer_name: Customer name or ID
            amount: Invoice amount
            description: Invoice description
            auto_post: Whether to post automatically or require approval
            
        Returns:
            Invoice creation result
        """
        if not self.authenticated:
            # Demo mode
            print(f"[DEMO] Would create invoice:")
            print(f"  Customer: {customer_name}")
            print(f"  Amount: ${amount:.2f}")
            print(f"  Description: {description}")
            
            self._log_action('invoice_demo', {
                'customer': customer_name,
                'amount': amount,
                'description': description
            }, 'demo')
            
            return {'demo': True, 'customer': customer_name, 'amount': amount}
        
        # Production: Create invoice via Odoo API
        # This requires finding customer ID first, then creating account.move
        
        result = self._json_rpc_call('res.partner', 'search_read', [
            [('name', '=', customer_name)]
        ], {'fields': ['id'], 'limit': 1})
        
        if result.get('error'):
            return result
        
        if not result.get('result'):
            return {'error': 'Customer not found'}
        
        customer_id = result['result'][0]['id']
        
        # Create invoice
        invoice_data = {
            'move_type': 'out_invoice',
            'partner_id': customer_id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount
                })
            ]
        }
        
        result = self._json_rpc_call('account.move', 'create', [invoice_data])
        
        if result.get('result'):
            invoice_id = result['result']
            self._log_action('invoice_created', {
                'invoice_id': invoice_id,
                'customer': customer_name,
                'amount': amount
            }, 'success')
            
            return {'success': True, 'invoice_id': invoice_id}
        
        return result
    
    def record_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_date: str = None,
        reference: str = None
    ) -> Dict[str, Any]:
        """Record a payment against an invoice."""
        if not self.authenticated:
            print(f"[DEMO] Would record payment:")
            print(f"  Invoice ID: {invoice_id}")
            print(f"  Amount: ${amount:.2f}")
            return {'demo': True}
        
        # Production: Create payment via Odoo API
        payment_data = {
            'amount': amount,
            'payment_date': payment_date or datetime.now().strftime('%Y-%m-%d'),
            'payment_reference': reference or ''
        }
        
        result = self._json_rpc_call('account.payment.register', 'create', [payment_data])
        
        return result
    
    def get_financial_report(
        self,
        report_type: str = 'profit_loss',
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """Get financial report from Odoo."""
        if not self.authenticated:
            return {'demo': {'revenue': 0, 'expenses': 0, 'profit': 0}}
        
        # Production: Call Odoo reporting APIs
        return self._json_rpc_call('account.report', 'get_report', [])
    
    def _log_action(self, action_type: str, data: dict, result: str):
        """Log action to audit log."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'odoo_mcp',
            'parameters': data,
            'result': result
        }
        
        log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        entries = []
        if log_file.exists():
            try:
                entries = json.loads(log_file.read_text())
            except:
                pass
        
        entries.append(log_entry)
        log_file.write_text(json.dumps(entries, indent=2))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, help='Action: create_invoice, record_payment, get_report')
    parser.add_argument('--customer', type=str, help='Customer name')
    parser.add_argument('--amount', type=float, help='Amount')
    parser.add_argument('--vault', type=str, default='Vault')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("ODOO MCP SERVER - GOLD TIER")
    print("="*60)
    
    mcp = OdooMCP(args.vault)
    
    if args.action == 'create_invoice':
        if not args.customer or not args.amount:
            print("\nUsage: python odoo_mcp.py --action create_invoice --customer \"Name\" --amount 1000")
            return
        result = mcp.create_invoice(args.customer, args.amount)
        print(f"\nResult: {result}")
        
    elif args.action == 'record_payment':
        print("\nPayment recording not fully implemented")
        
    elif args.action == 'get_report':
        result = mcp.get_financial_report()
        print(f"\nReport: {result}")
        
    else:
        print("\nUsage:")
        print("  python odoo_mcp.py --action create_invoice --customer \"Name\" --amount 1000")
        print("  python odoo_mcp.py --action get_report")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
