import os
import json
import secrets

import grpc
import KeyTransfer_pb2
import KeyTransfer_pb2_grpc

class KeyReleaseAgent:
    qkd_dir = ''
    sites = dict()
    seqID = 1

    sim_key_bank = list();
    key_bit_size = 32;
    keys_per_file = 4096;

    current_file_id = 0;
    keys_in_current_file = 0;
    bit_to_key_ineffiency = 2;

    def __init__(self, qkd_dir, sites, sim_key_bank = [], key_bit_size = 32, bit_to_key_ineffiency =2, keys_per_file = 4096):
        sites.sort()
        self.qkd_dir = qkd_dir
        self.sim_key_bank = sim_key_bank;
        if(key_bit_size % 8 == 0):
            self.key_bit_size = key_bit_size;
        else:
            raise Exception("Key bit size must be divisible by 8")

        self.keys_per_file = keys_per_file;

        self.bit_to_key_ineffiency = bit_to_key_ineffiency;

        # Get the site stubs for sending keys
        port = "50051"
        for site in sites:
            channel_url = f"localhost:{port}"
            qkdlink_path = os.path.join(
                self.qkd_dir, 
                "qnl/qll/keys/",
                site,
                "qkdlink.json"
            )
            if os.path.exists(qkdlink_path):
                with open(qkdlink_path, 'r') as qkdlink_file:
                    qkdlink_data = json.load(qkdlink_file)
                    remote_ip = qkdlink_data['remoteSiteAgentUrl'].split(':')[0]
                    channel_url = f"{remote_ip}:{port}"
            channel = grpc.insecure_channel(channel_url)
            self.sites[site] = {
                "channel": channel,
                "stub": KeyTransfer_pb2_grpc.KeyTransferStub(channel),
                "localID": f"{'_'.join(sites)}_{site}",
            }

    def append_to_key_bank(self, additional_keys):
        self.sim_key_bank.append(additional_keys);

    def get_n_keys(self, n):
        key_byte_size = self.key_bit_size // 8
        keys = [secrets.token_bytes(key_byte_size) for _ in range(n)]
        return keys;

    def releaseKeys(self, bits):
        num_keys = bits//(self.key_bit_size*self.bit_to_key_ineffiency);
        left_over_bits = bits%(self.key_bit_size*self.bit_to_key_ineffiency);
        
        keys = self.get_n_keys(num_keys);

        print(f"Releasing {num_keys} keys...")
        def send_keys():
            for key in keys:
                for site in self.sites.values():
                    stub = KeyTransfer_pb2_grpc.KeyTransferStub(site["channel"])
                    self.send_key(
                        stub=stub, 
                        key=key,
                        seqID=self.seqID,
                        localID=site['localID']
                    )
                    self.seqID += 1
        send_keys()

        return left_over_bits;

    def write_keys_to_file(self, file, write_type, keys):
        with open(file+str(self.current_file_id), write_type) as key_file:
            key_file.writelines(keys)

    def send_key(self, stub, key, seqID, localID):
        stub.OnKeyFromSatellite(
            KeyTransfer_pb2.Key(
                key=key,
                seqID=seqID,
                localID=localID
            )
        )
